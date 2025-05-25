import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class AssetType(str, enum.Enum):
    text = "text"
    image = "image"
    audio = "audio"


class SidePosition(str, enum.Enum):
    front = "front"
    back = "back"


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[AssetType] = mapped_column(Enum(AssetType))
    path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    sides: Mapped[list["CardSide"]] = relationship(
        back_populates="asset", cascade="all,delete"
    )


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    due_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    interval: Mapped[int] = mapped_column(Integer, default=0)
    ease_factor: Mapped[float] = mapped_column(Numeric(3, 2), default=2.5)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)

    sides: Mapped[list["CardSide"]] = relationship(
        back_populates="card", cascade="all,delete"
    )
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="card", cascade="all,delete"
    )
    tags: Mapped[list["Tag"]] = relationship(
        secondary="card_tags", back_populates="cards"
    )


class CardSide(Base):
    __tablename__ = "card_sides"
    __table_args__ = (UniqueConstraint("card_id", "position"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    card_id: Mapped[int] = mapped_column(
        ForeignKey("cards.id", ondelete="CASCADE")
    )
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE")
    )
    position: Mapped[SidePosition] = mapped_column(Enum(SidePosition))
    sort_order: Mapped[int] = mapped_column(Integer, default=1)

    card: Mapped["Card"] = relationship(back_populates="sides")
    asset: Mapped["Asset"] = relationship(back_populates="sides")


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    card_id: Mapped[int] = mapped_column(
        ForeignKey("cards.id", ondelete="CASCADE")
    )
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    rating: Mapped[int] = mapped_column(Integer)  # 0-5

    card: Mapped["Card"] = relationship(back_populates="reviews")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)

    cards: Mapped[list["Card"]] = relationship(
        secondary="card_tags", back_populates="tags"
    )


class CardTag(Base):
    __tablename__ = "card_tags"
    card_id: Mapped[int] = mapped_column(
        ForeignKey("cards.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )
