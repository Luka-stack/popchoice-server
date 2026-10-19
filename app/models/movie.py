from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
