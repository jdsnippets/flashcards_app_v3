import httpx

API = "http://127.0.0.1:8000"

def create_flashcard(front, back, tags):
    # Upload front asset
    front_files = {
        "type": (None, "text"),
        "file": ("front.txt", front, "text/plain"),
    }
    front_res = httpx.post(f"{API}/assets", files=front_files)
    front_res.raise_for_status()
    front_asset = front_res.json()

    # Upload back asset
    back_files = {
        "type": (None, "text"),
        "file": ("back.txt", back, "text/plain"),
    }
    back_res = httpx.post(f"{API}/assets", files=back_files)
    back_res.raise_for_status()
    back_asset = back_res.json()

    # Create card
    payload = {
        "front_asset_id": front_asset["id"],
        "back_asset_id": back_asset["id"],
        "tags": tags
    }
    card_res = httpx.post(f"{API}/cards", json=payload)
    card_res.raise_for_status()
    print("✅ Created card:", front[:60], "...")

def main():
    create_flashcard("How do you sync your uv project dependencies to match your lockfile?",
                     "uv sync", ["uv"])
    create_flashcard("How do you create a virtual environment using Python 3.13.3 with uv?",
                     "uv venv .venv --python 3.13.3", ["uv"])
    create_flashcard("How do you install FastAPI and other backend dependencies using uv?",
                     "uv add fastapi uvicorn pillow python-multipart sqlalchemy aiosqlite", ["uv"])
    create_flashcard("How do you upgrade uv to the latest version?",
                     "uv self update", ["uv"])
    create_flashcard("How do you set your Git username for this project to jdsnippets?",
                     'git config user.name "jdsnippets"', ["git"])
    create_flashcard("How do you run a FastAPI app with uvicorn and auto-reload enabled (using uv)?",
                     "uv run uvicorn backend.main:app --reload --reload-exclude .venv", ["uv"])
    create_flashcard("How do you install your local project in editable dev mode using uv?",
                     "uv add --editable . --dev", ["uv"])
    create_flashcard("How do you inspect the Git configuration for the current project?",
                     "cat .git/config", ["git"])
    create_flashcard("How do you initialize a new Python project with uv?",
                     "uv init <project_name>", ["uv"])
    create_flashcard("How do you activate a uv-created virtual environment?",
                     "source .venv/bin/activate", ["uv"])
    create_flashcard("How do you set your global Git username to neuroskipper?",
                     'git config --global user.name "neuroskipper"', ["git"])
    create_flashcard("How do you lock your project's dependencies with uv for reproducibility?",
                     "uv lock", ["uv"])
    create_flashcard("How do you install Python 3.13.3 using uv?",
                     "uv python install 3.13.3", ["uv"])
    create_flashcard('cli/shell command to find and delete all "__bak*" files under the current dir',
                     'find . -name "__bak*" -type f -delete', ["shell"])
    create_flashcard("how do you see what has been modified but not yet staged in git?",
                     "git diff", ["git"])

if __name__ == '__main__':
    main()
