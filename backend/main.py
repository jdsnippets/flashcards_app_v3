from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(title="Flashcards App v3", version="0.1.0")

# -- CORS (wide open for now; tighten when we add auth) ---------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -- Serve raw uploads & any other static assets ----------------------
STATIC_DIR = Path(__file__).parent.parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# --------------------------------------------------------------------
@app.get("/", tags=["system"])
async def root():
    """Health-check & hello."""
    return {"message": "Hello from Flashcards App v3 🚀"}
