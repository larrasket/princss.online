#!/usr/bin/env python3
"""
Generate backlinks.json mapping org IDs to their backlinks.
Scans Hugo content and old blog content for [[id:...]] links.
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict

# Directories to scan
HUGO_CONTENT_DIR = Path("/Users/l/roam/hugo/content")
BLOG_CONTENT_DIR = Path("/Users/l/blog/content")

# ID mapping files
HUGO_IDS_FILE = Path("/Users/l/roam/hugo/oldblog/hugo_ids.json")
BLOG_IDS_FILE = Path("/Users/l/roam/hugo/data/blog_ids.json")

# Output file
OUTPUT_FILE = Path("/Users/l/roam/hugo/data/backlinks.json")


def load_json(path):
    """Load JSON file, return empty dict if not found."""
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def get_org_id(content):
    """Extract :ID: from org file content."""
    match = re.search(r':ID:\s+(\S+)', content)
    return match.group(1) if match else None


def get_org_title(content):
    """Extract #+title: from org file content and clean it."""
    match = re.search(r'#\+title:\s*"?([^"\n]+)"?', content, re.IGNORECASE)
    if match:
        title = match.group(1).strip()
        # Clean org link syntax: [[id:...][text]] -> text, [[id:...]] -> remove
        title = re.sub(r'\[\[id:[^\]]+\]\[([^\]]+)\]\]', r'\1', title)
        title = re.sub(r'\[\[id:[^\]]+\]\]', '', title)
        # Clean external links: [[url][text]] -> text
        title = re.sub(r'\[\[[^\]]+\]\[([^\]]+)\]\]', r'\1', title)
        return title.strip()
    # Fallback: try TITLE property
    match = re.search(r':TITLE:\s+(.+)', content)
    return match.group(1).strip() if match else None


def find_id_links(content):
    """Find all [[id:...]] or [[id:...][...]] links in content."""
    # Pattern matches both [[id:xyz]] and [[id:xyz][description]]
    pattern = r'\[\[id:([^\]\[]+?)(?:\]\[([^\]]+))?\]\]'
    matches = re.findall(pattern, content)
    # Return list of target IDs
    return [match[0] for match in matches]


def scan_org_files(directory, id_mapping, is_blog=False):
    """
    Scan org files in directory.
    Returns:
        - files_info: dict of {id: {title, url, file_path, is_blog}}
        - links: list of (source_id, target_id) tuples
    """
    files_info = {}
    links = []
    
    if not directory.exists():
        print(f"Warning: Directory not found: {directory}")
        return files_info, links
    
    for org_file in directory.rglob("*.org"):
        try:
            with open(org_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {org_file}: {e}")
            continue
        
        org_id = get_org_id(content)
        if not org_id:
            continue
        
        title = get_org_title(content) or org_file.stem
        
        # Get URL from mapping
        url = id_mapping.get(org_id)
        if url and is_blog:
            # Blog URLs need /~saleh prefix and #ID anchor
            url = f"/~saleh{url}#{org_id}"
        
        files_info[org_id] = {
            'title': title,
            'url': url,
            'file_path': str(org_file),
            'is_blog': is_blog
        }
        
        # Find links in this file
        target_ids = find_id_links(content)
        for target_id in target_ids:
            links.append((org_id, target_id))
    
    return files_info, links


def build_backlinks(all_files_info, all_links):
    """
    Build backlinks mapping: {target_id: [{source_id, title, url}, ...]}
    Deduplicates by source_id to avoid multiple backlinks from the same file.
    """
    backlinks = defaultdict(dict)  # Use dict for deduplication by source_id
    
    for source_id, target_id in all_links:
        if source_id not in all_files_info:
            continue
        
        source_info = all_files_info[source_id]
        if not source_info.get('url'):
            continue  # Skip if we can't resolve the URL
        
        # Only add if not already present (deduplicate)
        if source_id not in backlinks[target_id]:
            backlinks[target_id][source_id] = {
                'id': source_id,
                'title': source_info['title'],
                'url': source_info['url']
            }
    
    # Convert to list format
    return {k: list(v.values()) for k, v in backlinks.items()}


def main():
    print("Loading ID mappings...")
    hugo_ids = load_json(HUGO_IDS_FILE)
    blog_ids = load_json(BLOG_IDS_FILE)
    
    print(f"Loaded {len(hugo_ids)} Hugo IDs, {len(blog_ids)} blog IDs")
    
    all_files_info = {}
    all_links = []
    
    # Scan Hugo content
    print(f"Scanning Hugo content: {HUGO_CONTENT_DIR}")
    hugo_files, hugo_links = scan_org_files(HUGO_CONTENT_DIR, hugo_ids, is_blog=False)
    all_files_info.update(hugo_files)
    all_links.extend(hugo_links)
    print(f"  Found {len(hugo_files)} files with IDs, {len(hugo_links)} links")
    
    # Scan blog content
    print(f"Scanning blog content: {BLOG_CONTENT_DIR}")
    blog_files, blog_links = scan_org_files(BLOG_CONTENT_DIR, blog_ids, is_blog=True)
    all_files_info.update(blog_files)
    all_links.extend(blog_links)
    print(f"  Found {len(blog_files)} files with IDs, {len(blog_links)} links")
    
    # Build backlinks
    print("Building backlinks...")
    backlinks = build_backlinks(all_files_info, all_links)
    
    # Count how many IDs have backlinks
    ids_with_backlinks = sum(1 for bl in backlinks.values() if bl)
    total_backlinks = sum(len(bl) for bl in backlinks.values())
    print(f"Generated {total_backlinks} backlinks for {ids_with_backlinks} IDs")
    
    # Write output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(backlinks, f, indent=2, ensure_ascii=False)
    
    print(f"Wrote backlinks to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
