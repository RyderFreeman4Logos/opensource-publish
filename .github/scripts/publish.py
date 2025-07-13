# Copyright (C) 2025 RyderFreeman4Logos
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import json
import re
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator

# --- Constants ---
CONFIG_FILE = 'config.json'
MANUSCRIPTS_DIR = 'manuscripts'
CONTENT_DIR = 'content'
FEED_FILE = 'static/feed.xml'

def main():
    """
    Main function to process manuscripts and generate the feed.
    """
    # --- Ensure content directory exists ---
    os.makedirs(CONTENT_DIR, exist_ok=True)

    # --- Load Config ---
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{CONFIG_FILE}' not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{CONFIG_FILE}'.")
        exit(1)

    author_name = config.get('authorName', 'Unknown Author')
    work_title = config.get('workTitle', 'Untitled Work')
    base_site_url = config.get('baseSiteUrl', '').strip('/')
    feed_link = config.get('feedLink', '')

    # --- Process all .txt files in manuscripts directory ---
    # The workflow is triggered by changes in this dir, so we process all
    # files to ensure consistency.
    for filename in os.listdir(MANUSCRIPTS_DIR):
        if not filename.endswith('.txt'):
            continue

        txt_path = os.path.join(MANUSCRIPTS_DIR, filename)
        
        match = re.match(r'^(\d{8,})\s+(.*)\.txt$', filename)
        if not match:
            print(f"Skipping invalid filename format: {filename}")
            continue
        
        chapter_id = match.group(1)
        chapter_title = match.group(2)
        
        # Create a URL-friendly slug for the filename
        slug = re.sub(r'[^\w-]', '', chapter_title.lower().replace(' ', '-'))
        md_filename = f"{chapter_id}-{slug}.md"
        md_path = os.path.join(CONTENT_DIR, md_filename)

        with open(txt_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        # Convert to basic Markdown with <p> tags for paragraphs
        md_content = f"# {chapter_title}\n\n"
        paragraphs = raw_content.strip().split('\n\n')
        md_content += "\n\n".join(f"<p>{p.strip()}</p>" for p in paragraphs if p.strip())

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"Processed '{filename}' to '{md_filename}'")

    # --- Generate Atom Feed from all Markdown files ---
    fg = FeedGenerator()
    fg.id(base_site_url or work_title)
    fg.title(work_title)
    fg.author({'name': author_name})
    if base_site_url:
        fg.link(href=base_site_url, rel='alternate')
    if feed_link:
        fg.link(href=feed_link, rel='self')
    fg.subtitle(f'The latest chapters of {work_title}.')
    fg.language('zh-CN')

    all_chapters = []
    for md_file in sorted(os.listdir(CONTENT_DIR)):
        if not md_file.endswith('.md'):
            continue
            
        md_path = os.path.join(CONTENT_DIR, md_file)
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        match = re.match(r'^(\d{8,})-(.*)\.md$', md_file)
        if match:
            # Reconstruct title from slug
            title_from_slug = match.group(2).replace('-', ' ').replace('_', ' ').title()
            all_chapters.append({
                'id': match.group(1),
                'title': title_from_slug,
                'content': content,
                'path': md_path,
                'filename': md_file
            })

    # Add entries to the feed, sorted by chapter ID
    for chapter in sorted(all_chapters, key=lambda x: x['id']):
        fe = fg.add_entry()
        entry_url = f"{base_site_url}/content/{chapter['filename']}" if base_site_url else f"urn:uuid:{chapter['id']}"
        fe.id(entry_url)
        fe.title(chapter['title'])
        fe.link(href=entry_url)
        fe.content(chapter['content'], type='html')
        # Use file modification time for the update timestamp
        fe.updated(datetime.fromtimestamp(os.path.getmtime(chapter['path']), tz=timezone.utc))

    fg.atom_file(FEED_FILE, pretty=True)
    print(f"Generated feed at '{FEED_FILE}'")

if __name__ == "__main__":
    main()
