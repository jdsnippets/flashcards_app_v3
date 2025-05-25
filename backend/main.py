from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from backend.database import Base, engine
from backend.routers.assets import router as assets_router
from backend.routers.cards import router as cards_router
from backend.routers.reviews import router as reviews_router
from fastapi.responses import FileResponse




app = FastAPI(title="Flashcards App v3", version="0.1.0")

app.include_router(assets_router)
app.include_router(cards_router)
app.include_router(reviews_router)

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


# Auto-create tables for now; we’ll switch to Alembic once migrations are in place
@app.on_event("startup")
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# --------------------------------------------------------------------
@app.get("/", include_in_schema=False)
async def serve_frontend():
    """
    Serve the Single-Page App entry point.
    """
    index_path = Path(__file__).parent.parent / "frontend" / "index.html"
    return FileResponse(index_path)



#--tbdeleted--|@app.get("/", tags=["system"])
#--tbdeleted--|async def root():
#--tbdeleted--|    """Health-check & hello."""
#--tbdeleted--|    return {"message": "Hello from Flashcards App v3 🚀"}

