\# Flashcards App v3

FastAPI + vanilla JS + Tailwind playground for multimodal flashcards
(text, image, audio) with spaced-repetition.

## Quick start

```bash
uv python install 3.13.3
uv venv .venv --python 3.13.3
source .venv/bin/activate

uv add fastapi uvicorn sqlalchemy aiosqlite python-multipart
uv lock

uv run uvicorn backend.main:app --reload --reload-exclude .venv
