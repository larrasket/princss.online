#!/bin/bash
# Pre-build script to expand #+INCLUDE directives using Emacs
# Run this before `hugo` to ensure all includes are expanded

set -e

HUGO_DIR="$(cd "$(dirname "$0")" && pwd)"
CONTENT_DIR="$HUGO_DIR/content"

echo "Expanding includes in org files..."

# Find all org files with #+INCLUDE or {{{inc
files_with_includes=$(grep -rEl "(#\+INCLUDE|\{\{\{inc)" "$CONTENT_DIR" 2>/dev/null || true)

if [ -z "$files_with_includes" ]; then
    echo "No files with includes found."
    exit 0
fi

for file in $files_with_includes; do
    echo "Processing: $file"

    # Use Emacs to expand includes
    emacs --batch \
        --eval "(require 'org)" \
        --eval "(require 'ox)" \
        --eval "(find-file \"$file\")" \
        --eval "(org-macro-initialize-templates)" \
        --eval "(org-macro-replace-all org-macro-templates)" \
        --eval "(org-export-expand-include-keyword)" \
        --eval "(save-buffer)" \
        --kill 2>/dev/null || echo "  Warning: Could not process $file"
done

echo "Done expanding includes."
echo "Now run: hugo"
