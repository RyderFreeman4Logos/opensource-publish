# Copyright (C) 2025 RyderFreeman4Logos
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import os
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
# Check if feedgen is installed
try:
    from feedgen.feed import FeedGenerator
except ImportError:
    print("Error: 'feedgen' module not found. Please install it.")
    exit(1)

# --- Constants ---
CONFIG_FILE = 'config.json'
MANUSCRIPTS_DIR = 'manuscripts'
CONTENT_DIR = 'content'
FEED_FILE = 'static/feed.xml'
INDEX_FILE = 'content/index.md'

def get_git_info():
    """
    Retrieve repository owner and name from git config or environment variables.
    """
    # Try GITHUB_REPOSITORY env var first (available in Actions)
    repo_slug = os.environ.get('GITHUB_REPOSITORY')
    if repo_slug:
        parts = repo_slug.split('/')
        if len(parts) == 2:
            return parts[0], parts[1]
    
    # Fallback to git command
    try:
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'], capture_output=True, text=True)
        url = result.stdout.strip()
        match = re.search(r'[:/]([\w-]+)/([\w-]+)(?:\.git)?$', url)
        if match:
            return match.group(1), match.group(2)
    except Exception:
        pass
    return None, None

def update_config_urls(config):
    """
    Updates config.json with auto-generated URLs if they are placeholders.
    Returns True if config was modified.
    """
    modified = False
    base_url = config.get('baseSiteUrl', '')
    
    # Check if we need to update
    needs_update = (
        not base_url 
        or '在此处填写' in base_url 
        or '自动生成' in base_url
        or not base_url.startswith('http')
    )
    
    if needs_update:
        owner, repo = get_git_info()
        if owner and repo:
            # Base URL points to the content directory for easier reading
            new_base_url = f"https://{owner}.github.io/{repo}/content"
            # Feed link points to the static file in root
            new_feed_link = f"https://{owner}.github.io/{repo}/static/feed.xml"
            
            if config.get('baseSiteUrl') != new_base_url or config.get('feedLink') != new_feed_link:
                config['baseSiteUrl'] = new_base_url
                config['feedLink'] = new_feed_link
                modified = True
                print(f"Auto-configured baseSiteUrl: {new_base_url}")
    
    return modified

def update_readme(config):
    """
    Swaps or updates the README.md based on config state.
    """
    readme_path = 'README.md'
    template_path = 'docs/README_TEMPLATE.md'
    
    if not os.path.exists(readme_path) or not os.path.exists(template_path):
        return

    with open(readme_path, 'r', encoding='utf-8') as f:
        current_content = f.read()

    # --- Config Values ---
    author = config.get('authorName', 'Author')
    title = config.get('workTitle', 'Title')
    desc = config.get('description', '')
    base_url = config.get('baseSiteUrl', '#')
    feed_link = config.get('feedLink', '#')
    community_link = config.get('communityLink', '')
    if '在此处填写' in community_link: community_link = ''

    # --- Scenario 1: Initial Swap ---
    # Trigger: Default README is present AND User has updated the config (Author Name is not placeholder)
    is_default_readme = "欢迎您使用本模板开始您的创作之旅" in current_content or "Quick Start" in current_content
    is_config_ready = "在此处填写" not in author
    
    if is_default_readme:
        if is_config_ready:
            print("Swapping default README with Book Cover template...")
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Initial replacement of placeholders
            new_content = template_content
            new_content = new_content.replace('{{authorName}}', author)
            new_content = new_content.replace('{{workTitle}}', title)
            new_content = new_content.replace('{{description}}', desc)
            
            # Construct links line for initial swap
            links_line = f"[📖 在线阅读]({base_url}) | [📡 订阅 RSS]({feed_link})"
            if community_link:
                links_line += f" | [💬 读者群]({community_link})"
            
            # Replace the whole links block in template
            # Template has:
            # <!-- links-start -->
            # ...
            # <!-- links-end -->
            new_content = re.sub(r'(<!-- links-start -->\n)(.*?)(\n<!-- links-end -->)', 
                                 fr'\1{links_line}\3', 
                                 new_content, flags=re.DOTALL)

            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        else:
            print("Config not ready (author name is placeholder). Skipping README swap.")
    
    # --- Scenario 2: Ongoing Update ---
    # Trigger: Markers exist in current README. We update content between markers.
    else:
        print("Updating existing README fields...")
        new_content = current_content
        
        # Helper to replace between markers
        def replace_field(text, key, value):
            pattern = fr'(<!-- {key}-start -->)(.*?)(<!-- {key}-end -->)'
            return re.sub(pattern, fr'\1{value}\3', text, flags=re.DOTALL)

        new_content = replace_field(new_content, 'title', title)
        new_content = replace_field(new_content, 'author', author)
        new_content = replace_field(new_content, 'description', desc)
        
        # Construct the links line
        links_line = f"[📖 在线阅读]({base_url}) | [📡 订阅 RSS]({feed_link})"
        if community_link:
            links_line += f" | [💬 读者群]({community_link})"
        
        # Replace links block (multi-line)
        new_content = re.sub(r'(<!-- links-start -->\n)(.*?)(\n<!-- links-end -->)', 
                             fr'\1{links_line}\3', 
                             new_content, flags=re.DOTALL)

        if new_content != current_content:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("README.md updated with new config values.")

def get_git_updated_time(filepath):
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%at', '--', filepath],
            capture_output=True, text=True, check=False
        )
        timestamp = result.stdout.strip()
        if timestamp:
            return datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
    except Exception:
        pass
    return datetime.fromtimestamp(os.path.getmtime(filepath), tz=timezone.utc)

def main():
    """
    Main function.
    """
    # --- Fix 1: Clean Content Directory ---
    if os.path.exists(CONTENT_DIR):
        try:
            # We preserve index.md? No, script generates it.
            # We preserve .gitkeep? Not strictly necessary.
            shutil.rmtree(CONTENT_DIR)
            print(f"Cleaned {CONTENT_DIR} directory.")
        except Exception as e:
            print(f"Warning: Could not clean content dir: {e}")
            
    os.makedirs(CONTENT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(FEED_FILE), exist_ok=True)

    # --- Load Config ---
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}

    # --- Auto-Update Config ---
    if update_config_urls(config):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print("Updated config.json with auto-generated URLs.")
        except Exception as e:
            print(f"Warning: Could not save updated config.json: {e}")

    # --- Auto-Update README ---
    update_readme(config)

    author_name = config.get('authorName', 'Unknown Author')
    work_title = config.get('workTitle', 'Untitled Work')
    description = config.get('description', '')
    base_site_url = config.get('baseSiteUrl', '').strip('/')
    feed_link = config.get('feedLink', '')

    # --- Load Donation Info ---
    donation_html = ""
    donation_path = os.path.join(MANUSCRIPTS_DIR, 'donation.txt')
    if os.path.exists(donation_path):
        with open(donation_path, 'r', encoding='utf-8') as f:
            raw_donation = f.read()
            # Simple Markdown to HTML conversion
            donation_content = re.sub(r'^### (.*)', r'<h3>\1</h3>', raw_donation, flags=re.MULTILINE)
            donation_content = re.sub(r'^## (.*)', r'<h2>\1</h2>', donation_content, flags=re.MULTILINE)
            donation_content = re.sub(r'^# (.*)', r'<h1>\1</h1>', donation_content, flags=re.MULTILINE)
            donation_content = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank">\1</a>', donation_content)
            donation_content = re.sub(r'`(.*?)`', r'<code>\1</code>', donation_content)
            donation_content = donation_content.replace('\n', '<br>')
            
            donation_html = f"""
<div id="donation-section" style="text-align: center; margin: 40px 0;">
    <button onclick="document.getElementById('donation-modal').style.display='block'" 
            style="background-color: #d73a49; color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold;">
        🎁 打赏催更 / Support Author
    </button>
</div>

<div id="donation-modal" style="display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.4);">
    <div style="background-color: #fefefe; margin: 15% auto; padding: 20px; border: 1px solid #888; width: 80%; max-width: 600px; border-radius: 8px; position: relative;">
        <span onclick="document.getElementById('donation-modal').style.display='none'" 
              style="color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer;">&times;</span>
        <div style="margin-top: 20px; line-height: 1.6;">
            {donation_content}
        </div>
    </div>
</div>
<script>
window.onclick = function(event) {{
    var modal = document.getElementById('donation-modal');
    if (event.target == modal) {{
        modal.style.display = "none";
    }}
}}
</script>
"""

    # --- Collect Chapters ---
    chapters = []
    files = sorted([f for f in os.listdir(MANUSCRIPTS_DIR) if f.endswith('.txt') and f != 'donation.txt'])

    for filename in files:
        txt_path = os.path.join(MANUSCRIPTS_DIR, filename)
        match = re.match(r'^(\d+)[_\.\s]+(.*)\.txt$', filename)
        if not match:
            print(f"Skipping invalid filename format: {filename}")
            continue
        
        chapter_id = match.group(1)
        chapter_title = match.group(2).strip()
        slug = re.sub(r'[^\w\u4e00-\u9fa5-]', '', chapter_title.replace(' ', '-'))
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
        prev_chapter = chapters[i-1] if i > 0 else None
        next_chapter = chapters[i+1] if i < len(chapters) - 1 else None

        with open(chapter['txt_path'], 'r', encoding='utf-8') as f:
            raw_content = f.read()

        content = raw_content.replace('\r\n', '\n')
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if len(paragraphs) <= 1 and len(content) > 100:
             paragraphs = [p.strip() for p in content.split('\n') if p.strip()]

        md_content = "---\n"
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
        md_content += "---\n"

        md_content += f"\n# {chapter['title']}\n\n"
        md_content += "\n\n".join(f"{p}" for p in paragraphs)
        
        if donation_html:
            md_content += f"\n\n{donation_html}\n\n"
        
        md_content += "\n\n---\n"
        md_content += "\n<div class=\"navigation\">\n"
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

        md_path = os.path.join(CONTENT_DIR, chapter['md_filename'])
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"Generated {chapter['md_filename']}")

    # --- Generate Index (Table of Contents) ---
    index_content = "---\n"
    index_content += "layout: default\n"
    index_content += f"title: \"{work_title}\"\n"
    index_content += "---\n"

    index_content += f"\n# {work_title}\n\n"
    if description:
        index_content += f"*{description}*\n\n"
    
    community_link = config.get('communityLink', '')
    if community_link and '在此处填写' not in community_link:
        index_content += f"[💬 加入读者交流群]({community_link})\n\n"

    index_content += "---\n"

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

    for chapter in reversed(chapters):
        fe = fg.add_entry()
        entry_url = f"{base_site_url}/{chapter['md_filename']}" if base_site_url else f"urn:chapter:{chapter['id']}"
        fe.id(entry_url)
        fe.title(chapter['title'])
        fe.link(href=entry_url)
        fe.summary(f"New chapter available: {chapter['title']}. Click to read.")
        fe.updated(chapter['updated_at'])

    fg.atom_file(FEED_FILE, pretty=True)
    print(f"Generated feed at '{FEED_FILE}'")

if __name__ == "__main__":
    main()