# Copyright (C) 2025 RyderFreeman4Logos
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import os
import json
import re
import subprocess
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator

# --- Constants ---
CONFIG_FILE = 'config.json'
MANUSCRIPTS_DIR = 'manuscripts'
CONTENT_DIR = 'content'
FEED_FILE = 'static/feed.xml'
INDEX_FILE = 'content/index.md'

def get_git_updated_time(filepath):
    """
    Get the last commit timestamp for a file.
    Falls back to filesystem modification time if git fails.
    """
    try:
        # Run git log to get the unix timestamp of the last commit
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%at', '--', filepath],
            capture_output=True, text=True, check=False
        )
        timestamp = result.stdout.strip()
        if timestamp:
            return datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
    except Exception as e:
        print(f"Warning: git log failed for {filepath}: {e}")
    
    return datetime.fromtimestamp(os.path.getmtime(filepath), tz=timezone.utc)

def main():
    """
    Main function to process manuscripts and generate the feed.
    """
    os.makedirs(CONTENT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(FEED_FILE), exist_ok=True)

    # --- Load Config ---
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}

    author_name = config.get('authorName', 'Unknown Author')
    work_title = config.get('workTitle', 'Untitled Work')
    description = config.get('description', '')
    base_site_url = config.get('baseSiteUrl', '').strip('/')
    feed_link = config.get('feedLink', '')

    # --- Collect Chapters ---
    chapters = []
    
    # Filter and sort files
    files = sorted([f for f in os.listdir(MANUSCRIPTS_DIR) if f.endswith('.txt')])

    for filename in files:
        txt_path = os.path.join(MANUSCRIPTS_DIR, filename)
        
        # Regex to extract ID and Title
        # Supports: "001 Title.txt", "001_Title.txt", "001. Title.txt"
        match = re.match(r'^(\d+)[_\.\s]+(.*)\.txt$', filename)
        if not match:
            print(f"Skipping invalid filename format: {filename}")
            continue
        
        chapter_id = match.group(1)
        chapter_title = match.group(2).strip()
        
        # Create a URL-friendly slug
        slug = re.sub(r'[^\w\u4e00-\u9fa5-]', '', chapter_title.replace(' ', '-'))
        # Ensure distinct filename even if titles are same (using ID)
        md_filename = f"{chapter_id}-{slug}.md"
        
        chapters.append({
            'id': chapter_id,
            'title': chapter_title,
            'txt_path': txt_path,
            'md_filename': md_filename,
            'updated_at': get_git_updated_time(txt_path)
        })

    # --- Process Chapters & Generate Content ---
    for i, chapter in enumerate(chapters):
        # Determine Next/Prev
        prev_chapter = chapters[i-1] if i > 0 else None
        next_chapter = chapters[i+1] if i < len(chapters) - 1 else None

        with open(chapter['txt_path'], 'r', encoding='utf-8') as f:
            raw_content = f.read()

        # Better text processing
        # 1. Normalize line endings
        content = raw_content.replace('\r\n', '\n')
        # 2. Split by double newlines (paragraphs)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        # 3. If no double newlines found, try splitting by single newlines (common in some editors)
        if len(paragraphs) <= 1 and len(content) > 100:
             paragraphs = [p.strip() for p in content.split('\n') if p.strip()]

        # Generate Markdown with Front Matter
        md_content = "---\
"
        md_content += f"layout: default\n"
        md_content += f"title: \"{chapter['title']}\"\n"
        md_content += f"date: {chapter['updated_at'].isoformat()}\n"
        md_content += f"author: \"{author_name}\"\n"
        if prev_chapter:
            md_content += f"prev_url: ./ {prev_chapter['md_filename']}\n"
            md_content += f"prev_title: \"{prev_chapter['title']}\"\n"
        if next_chapter:
            md_content += f"next_url: ./ {next_chapter['md_filename']}\n"
            md_content += f"next_title: \"{next_chapter['title']}\"\n"
        md_content += "---\
\n"

        md_content += f"# {chapter['title']}\n\n"
        md_content += "\n\n".join(f"{p}" for p in paragraphs)
        
        # Add navigation footer
        md_content += "\n\n---\
\n"
        md_content += "<div class=\"navigation\">\n"
        if prev_chapter:
            md_content += f"  <a href=\"./{prev_chapter['md_filename']}\">← {prev_chapter['title']}</a>\n"
        else:
            md_content += "  <span></span>\n"
            
        md_content += f"  <a href=\"./index.md\">目录</a>\n"
        
        if next_chapter:
            md_content += f"  <a href=\"./{next_chapter['md_filename']}\">{next_chapter['title']} →</a>\n"
        else:
            md_content += "  <span></span>\n"
        md_content += "</div>\n"

        # Write MD file
        md_path = os.path.join(CONTENT_DIR, chapter['md_filename'])
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"Generated {chapter['md_filename']}")

    # --- Generate Index (Table of Contents) ---
    index_content = "---\
"
    index_content += "layout: default\n"
    index_content += f"title: \"{work_title}\"\n"
    index_content += "---\
\n"
    index_content += f"# {work_title}\n\n"
    if description:
        index_content += f"*{description}*\n\n"
    index_content += "---\
\n"
    index_content += "## 目录\n\n"
    
    for chapter in chapters:
        index_content += f"- [{chapter['title']}](./{chapter['md_filename']})\n"
        
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(index_content)
    print("Generated index.md")

    # --- Generate Atom Feed ---
    fg = FeedGenerator()
    fg.id(base_site_url or 'urn:uuid:00000000')
    fg.title(work_title)
    fg.author({'name': author_name})
    if base_site_url:
        fg.link(href=base_site_url, rel='alternate')
    if feed_link:
        fg.link(href=feed_link, rel='self')
    fg.subtitle(f'Latest chapters of {work_title}')
    fg.language('zh-CN')

    # Add entries (reverse chronological for feed is usually better, but for books ID order is also fine. 
    # Let's stick to ID order but maybe standard readers expect newest first? 
    # Actually for a book, you want the "newest published chapter" at the top usually.)
    for chapter in reversed(chapters):
        fe = fg.add_entry()
        entry_url = f"{base_site_url}/content/{chapter['md_filename']}" if base_site_url else f"urn:chapter:{chapter['id']}"
        fe.id(entry_url)
        fe.title(chapter['title'])
        fe.link(href=entry_url)
        
        # Read back the content we just wrote to get the HTML-ish markdown
        # Note: In a real robust setup we'd convert MD to HTML here for the feed content.
        # For now, we will provide a summary link.
        fe.summary(f"New chapter available: {chapter['title']}. Click to read.")
        fe.updated(chapter['updated_at'])

    fg.atom_file(FEED_FILE, pretty=True)
    print(f"Generated feed at '{FEED_FILE}'")

if __name__ == "__main__":
    main()