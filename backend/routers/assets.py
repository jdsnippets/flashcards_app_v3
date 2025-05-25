from fastapi import APIRouter, UploadFile, Form, Depends, HTTPException, Path as PathParam
from mutagen import File as MutagenFile
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_session
from backend.models import Asset, AssetType
from pydantic import BaseModel
from pathlib import Path
from uuid import uuid4
import shutil
from datetime import datetime

router = APIRouter(prefix="/assets", tags=["assets"])

UPLOAD_DIR = Path(__file__).parent.parent / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class AssetRead(BaseModel):
    id: int
    type: AssetType
    path: str
    duration: float | None = None
    text: str | None = None

    class Config:
        orm_mode = True


@router.get(
    "/{asset_id}",
    response_model=AssetRead,
    summary="Fetch a single asset by ID",
)
async def read_asset(
    asset_id: int = PathParam(..., description="The ID of the asset to retrieve"),
    session: AsyncSession = Depends(get_session),
):
    asset = await session.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

        
@router.post("", response_model=AssetRead)
async def upload_asset(
    file: UploadFile,
    type: AssetType = Form(...),
    session: AsyncSession = Depends(get_session),
):
    now = datetime.utcnow()
    folder = UPLOAD_DIR / f"{now.year}" / f"{now.month:02}"
    folder.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix
    filename = f"{uuid4().hex}{ext}"
    dest = folder / filename
    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    duration = None
    text_content = None

    if type == AssetType.audio:
        try:
            audio = MutagenFile(str(dest))
            if audio is None or not hasattr(audio, "info"):
                raise ValueError("Unsupported audio format")
            duration = round(audio.info.length, 2)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid audio file")
    elif type == AssetType.text:
        try:
            text_content = dest.read_text(encoding="utf-8")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid text file")

    asset = Asset(
        type=type,
        path=str(dest.relative_to(Path(__file__).parent.parent / "static")),
        duration=duration,
        text=text_content,
    )

    session.add(asset)
    await session.commit()
    await session.refresh(asset)

    return AssetRead.from_orm(asset)
