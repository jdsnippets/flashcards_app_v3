from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime, timedelta

from backend.database import get_session
from backend.models import Review, Card

router = APIRouter(prefix="/reviews", tags=["reviews"])

# --- SM-2 scheduler helper ----------------------------------------
def sm2(card: Card, rating: int) -> None:
    """Mutate card scheduling fields according to SM-2 algorithm."""
    # Convert ease_factor (Decimal) to float for arithmetic
    current_ef = float(card.ease_factor)

    # If the quality response is lower than 3, reset repetitions
    if rating < 3:
        card.repetitions = 0
        interval = 1
    else:
        card.repetitions += 1
        if card.repetitions == 1:
            interval = 1
        elif card.repetitions == 2:
            interval = 6
        else:
            interval = round(card.interval * current_ef)

    # Update ease factor using float arithmetic
    ef = current_ef + (0.1 - (5 - rating) * (0.08 + (5 - rating) * 0.02))
    card.ease_factor = max(1.3, ef)

    # Set new interval and due date
    card.interval = interval
    card.due_at = date.today() + timedelta(days=interval)

# --- Pydantic schemas ---------------------------------------------
class ReviewCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    card_id: int
    rating: int = Field(..., ge=0, le=5)

class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    card_id: int
    reviewed_at: datetime
    rating: int

# --- Endpoints -----------------------------------------------------
@router.post("", response_model=ReviewRead)
async def create_review(
    payload: ReviewCreate,
    session: AsyncSession = Depends(get_session),
):
    # Fetch card and validate
    card = await session.get(Card, payload.card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    # Apply SM-2 scheduling
    sm2(card, payload.rating)

    # Create review record
    review = Review(card_id=card.id, rating=payload.rating)
    session.add_all([card, review])
    await session.commit()
    await session.refresh(review)

    return ReviewRead.from_orm(review)
