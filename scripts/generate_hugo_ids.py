#!/usr/bin/env python3
"""
Generate hugo_ids.json mapping org IDs to Hugo URLs.
Run after Hugo build: scans public/ directory to get actual URLs.
"""

import json
import os
import re
from pathlib import Path

hugo_dir = Path("/Users/l/roam/hugo")
content_dir = hugo_dir / "content"
public_dir = hugo_dir / "public"
output_file = hugo_dir / "oldblog" / "hugo_ids.json"

def get_org_id(file_path):
    """Extract :ID: from org file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read(2000)  # ID is always near the top
    match = re.search(r':ID:\s+(\S+)', content)
    return match.group(1) if match else None

def get_hugo_url(content_path):
    """Get Hugo URL from content path by checking public directory structure."""
    rel_path = content_path.relative_to(content_dir)
    
    # Skip _index files
    if rel_path.stem == '_index':
        return None
    
    # Hugo's URL structure: /section/filename/
    parts = list(rel_path.parts)
    section = parts[0]
    filename = rel_path.stem
    
    # Check if the public directory exists for this
    public_path = public_dir / section / filename
    if public_path.is_dir() and (public_path / "index.html").exists():
        return f"/{section}/{filename}/"
    
    # For nested sections like music-pages/discoveries/
    if len(parts) > 2:
        nested_path = "/".join(parts[:-1])
        public_path = public_dir / nested_path / filename
        if public_path.is_dir() and (public_path / "index.html").exists():
            return f"/{nested_path}/{filename}/"
    
    return None

def main():
    mapping = {}
    
    for org_file in content_dir.rglob("*.org"):
        org_id = get_org_id(org_file)
        if org_id:
            url = get_hugo_url(org_file)
            if url:
                mapping[org_id] = url
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    
    print(f"Generated {len(mapping)} Hugo ID mappings to {output_file}")

if __name__ == "__main__":
    main()
