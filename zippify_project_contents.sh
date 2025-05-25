#!/bin/bash

# zippify_project_contents.sh
# -----------------------------------------
# Create a ZIP archive of relevant project files
# Excludes virtual environments, databases, cache, and lock files

OUTPUT_ZIP="flashcards_project_snapshot.zip"

echo "📦 Generating snapshot: $OUTPUT_ZIP"

zip -r "$OUTPUT_ZIP" \
  backend \
  frontend \
  scripts \
  alembic \
  pyproject.toml \
  zippify_project_contents.sh \
  --exclude '**/__pycache__/*' '*.db' '*.sqlite3' '*.log' '*.zip' '*.lock' '.venv/*'

echo "✅ Done. Snapshot saved as $OUTPUT_ZIP"
