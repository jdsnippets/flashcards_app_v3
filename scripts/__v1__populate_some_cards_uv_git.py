#!/usr/bin/env python3
"""
scripts/load_sample_data.py

Seed the v3 database with sample flashcards from your v2 data.

Usage:
    python3 scripts/load_sample_data.py

Pre-req:
  • Your virtualenv is active
  • You've run `alembic upgrade head`
"""
import sys
from pathlib import Path
import asyncio
from datetime import datetime

# ensure project root on PYTHONPATH
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session
from backend.models import (
    Asset, AssetType, Card, CardSide, SidePosition, Tag, CardTag
)

# Legacy flashcards with their tags.
# If you want dual tags (e.g. both "uv" and "git"), just list both in the "tags" list.
cards_data = [
    {
        "question": "How do you apply your lockfile changes to the virtual environment?",
        "answer": "uv sync",
        "tags": ["setup"],
    },
    {
        "question": "How do you create a virtual environment using Python 3.13.3?",
        "answer": "uv venv .venv --python 3.13.3",
        "tags": ["setup"],
    },
    {
        "question": "How do you add key backend dependencies like FastAPI and SQLite with uv?",
        "answer": "uv add fastapi uvicorn pillow python-multipart sqlalchemy aiosqlite",
        "tags": ["setup"],
    },
    {
        "question": "How do you update the uv tool to the latest version?",
        "answer": "uv self update",
        "tags": ["uv"],
    },
    {
        "question": "How do you set your project-specific Git username to 'jdsnippets'?",
        "answer": 'git config user.name "jdsnippets"',
        "tags": ["git"],
    },
    {
        "question": "How do you run a FastAPI app using uvicorn with auto-reload?",
        "answer": "uv run uvicorn backend.main:app --reload --reload-exclude .venv",
        "tags": ["setup"],
    },
    {
        "question": "How do you add the local project in editable mode for development?",
        "answer": "uv add --editable . --dev",
        "tags": ["setup"],
    },
    {
        "question": "How do you verify the current Git config file contents?",
        "answer": "cat .git/config",
        "tags": ["git"],
    },
    {
        "question": "What command initializes a new Python project using uv?",
        "answer": "uv init <project_name>",
        "tags": ["setup"],
    },
    {
        "question": "How do you activate a uv-created virtual environment?",
        "answer": "source .venv/bin/activate",
        "tags": ["setup"],
    },
    {
        "question": "What command sets your global Git username to 'neuroskipper'?",
        "answer": 'git config --global user.name "neuroskipper"',
        "tags": ["git"],
    },
    {
        "question": "What command locks your uv dependencies for reproducibility?",
        "answer": "uv lock",
        "tags": ["uv"],
    },
    {
        "question": "What command installs Python 3.13.3 using uv?",
        "answer": "uv python install 3.13.3",
        "tags": ["setup"],
    },
]

async def load_cards():
    async with get_session() as session:  # type: AsyncSession
        for item in cards_data:
            # 1. Create front (text) asset
            front = Asset(type=AssetType.text, text=item["question"])
            session.add(front)
            await session.flush()  # get front.id

            # 2. Create back (text) asset
            back = Asset(type=AssetType.text, text=item["answer"])
            session.add(back)
            await session.flush()   # get back.id

            # 3. Create card record
            card = Card()  # SM-2 fields default to interval=0, ease_factor=2.5, reps=0
            session.add(card)
            await session.flush()   # get card.id

            # 4. Create two sides
            session.add_all([
                CardSide(card_id=card.id, asset_id=front.id, position=SidePosition.front),
                CardSide(card_id=card.id, asset_id=back.id,  position=SidePosition.back),
            ])

            # 5. Handle tags (upsert)
            for tag_name in item["tags"]:
                name = tag_name.strip().lower()
                result = await session.execute(select(Tag).where(Tag.name == name))
                tag = result.scalar_one_or_none()
                if not tag:
                    tag = Tag(name=name)
                    session.add(tag)
                    await session.flush()
                # link card and tag
                session.add(CardTag(card_id=card.id, tag_id=tag.id))

        await session.commit()
        print(f"✅ Loaded {len(cards_data)} cards.")

if __name__ == "__main__":
    asyncio.run(load_cards())
