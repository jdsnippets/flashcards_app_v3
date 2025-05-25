from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, ConfigDict

from backend.database import get_session
from backend.models import Card, CardSide, Asset, Tag, CardTag, SidePosition

router = APIRouter(prefix="/cards", tags=["cards"])

class CardSideRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    position: SidePosition
    asset_id: int

class CardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    due_at: Optional[str]
    interval: int
    ease_factor: float
    repetitions: int
    sides: List[CardSideRead]
    tags: List[str]

class CardCreate(BaseModel):
    front_asset_id: int
    back_asset_id: int
    tags: Optional[List[str]] = []

@router.post("", response_model=CardRead)
async def create_card(
    payload: CardCreate,
    session: AsyncSession = Depends(get_session),
):
    # Validate assets exist
    front = await session.get(Asset, payload.front_asset_id)
    back = await session.get(Asset, payload.back_asset_id)
    if not front or not back:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Create card
    card = Card()
    session.add(card)
    await session.flush()

    # Create sides
    fs = CardSide(card_id=card.id, asset_id=front.id, position=SidePosition.front)
    bs = CardSide(card_id=card.id, asset_id=back.id, position=SidePosition.back)
    session.add_all([fs, bs])

    # Handle tags
    for name in payload.tags or []:
        name_lower = name.strip().lower()
        result = await session.execute(
            select(Tag).where(func.lower(Tag.name) == name_lower)
        )
        tag = result.scalar_one_or_none()
        if not tag:
            tag = Tag(name=name_lower)
            session.add(tag)
            await session.flush()
        session.add(CardTag(card_id=card.id, tag_id=tag.id))

    await session.commit()
    #--tbdeleted--|await session.refresh(card)
    #--fix: ok--|await session.refresh(card, attribute_names=["sides", "tags"])
    
    # Reload with relationships to avoid lazy loading issues
    card = (
        await session.execute(
            select(Card)
            .options(
                selectinload(Card.sides),
                selectinload(Card.tags)
            )
            .where(Card.id == card.id)
        )
    ).scalar_one()

    return CardRead(
        id=card.id,
        due_at=card.due_at.isoformat() if card.due_at else None,
        interval=card.interval,
        ease_factor=float(card.ease_factor),
        repetitions=card.repetitions,
        sides=[CardSideRead(position=s.position, asset_id=s.asset_id) for s in card.sides],
        tags=[t.name for t in card.tags],
    )

@router.get("", response_model=List[CardRead])
async def list_cards(
    tags: Optional[List[str]] = Query(None, description="Filter by tag names"),
    mode: str = Query("any", regex="^(any|all)$"),
    due_only: bool = Query(False, description="Only cards due today or earlier"),
    session: AsyncSession = Depends(get_session),
):
    # Eager-load relationships
    query = (
        select(Card)
        .options(
            selectinload(Card.sides),
            selectinload(Card.tags)
        )
        .distinct()
    )

    if due_only:
        query = query.where(Card.due_at <= func.current_date())

    if tags:
        query = query.join(CardTag).join(Tag)
        lowered = [t.strip().lower() for t in tags]
        if mode == "any":
            query = query.where(func.lower(Tag.name).in_(lowered))
        else:
            for name in lowered:
                query = query.where(
                    select(CardTag)
                    .where(CardTag.card_id == Card.id)
                    .join(Tag)
                    .where(func.lower(Tag.name) == name)
                    .exists()
                )

    result = (await session.execute(query)).scalars().all()

    return [
        CardRead(
            id=c.id,
            due_at=c.due_at.isoformat() if c.due_at else None,
            interval=c.interval,
            ease_factor=float(c.ease_factor),
            repetitions=c.repetitions,
            sides=[CardSideRead(position=s.position, asset_id=s.asset_id) for s in c.sides],
            tags=[t.name for t in c.tags],
        )
        for c in result
    ]
