#!/usr/bin/env python3
"""
scripts/populate_some_cards_uv_git.py

Seed the v3 database with sample flashcards (UV/GIT data).

Usage:
    python3 scripts/populate_some_cards_uv_git.py
Pre-req:
    • venv active
    • flashcards.db removed or empty, then `alembic upgrade head`
"""

import sys
import asyncio
from pathlib import Path

# Ensure project root on PYTHONPATH
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Import the async sessionmaker directly
from backend.database import AsyncSessionLocal
from backend.models import (
    Asset, AssetType, Card, CardSide, SidePosition, Tag, CardTag
)



cards_data = [
    {
        "question": "How do you apply your lockfile changes to the virtual environment?",
        "answer": "uv sync",
        "tags": ["uv"],
    },
    {
        "question": "How do you create a virtual environment using Python 3.13.3?",
        "answer": "uv venv .venv --python 3.13.3",
        "tags": ["uv"],
    },
    {
        "question": "How do you add key backend dependencies like FastAPI and SQLite with uv?",
        "answer": "uv add fastapi uvicorn pillow python-multipart sqlalchemy aiosqlite",
        "tags": ["uv"],
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
        "tags": ["uv"],
    },
    {
        "question": "How do you add the local project in editable mode for development?",
        "answer": "uv add --editable . --dev",
        "tags": ["uv"],
    },
    {
        "question": "How do you verify the current Git config file contents?",
        "answer": "cat .git/config",
        "tags": ["git"],
    },
    {
        "question": "What command initializes a new Python project using uv?",
        "answer": "uv init <project_name>",
        "tags": ["uv"],
    },
    {
        "question": "How do you activate a uv-created virtual environment?",
        "answer": "source .venv/bin/activate",
        "tags": ["uv"],
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
        "tags": ["uv"],
    },
]

#--tbdeleted--|cards_data = [
#--tbdeleted--|    {"question": "...lockfile changes?", "answer": "uv sync", "tags": ["setup"]},
#--tbdeleted--|    {"question": "...create venv ...?",   "answer": "uv venv .venv --python 3.13.3", "tags": ["setup"]},
#--tbdeleted--|    # ... rest of your 13 items ...
#--tbdeleted--|]

async def load_cards():
    # Use the session factory directly
    async with AsyncSessionLocal() as session:  # type: AsyncSession
        for item in cards_data:
            # 1) front asset
            front = Asset(type=AssetType.text, text=item["question"])
            session.add(front)
            await session.flush()

            # 2) back asset
            back = Asset(type=AssetType.text, text=item["answer"])
            session.add(back)
            await session.flush()

            # 3) card
            card = Card()
            session.add(card)
            await session.flush()

            # 4) sides
            session.add_all([
                CardSide(card_id=card.id, asset_id=front.id, position=SidePosition.front),
                CardSide(card_id=card.id, asset_id=back.id,  position=SidePosition.back),
            ])

            # 5) tags
            for tname in item["tags"]:
                name = tname.strip().lower()
                result = await session.execute(select(Tag).where(Tag.name == name))
                tag = result.scalar_one_or_none()
                if not tag:
                    tag = Tag(name=name)
                    session.add(tag)
                    await session.flush()
                session.add(CardTag(card_id=card.id, tag_id=tag.id))

        await session.commit()
        print(f"✅ Loaded {len(cards_data)} cards.")

if __name__ == "__main__":
    asyncio.run(load_cards())
