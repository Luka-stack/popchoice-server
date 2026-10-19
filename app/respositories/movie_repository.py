import logging
from sqlalchemy import text, bindparam
from sqlalchemy.ext.asyncio import AsyncSession
from pgvector.sqlalchemy import Vector

from app.models.movie import Movie

logger = logging.getLogger(__name__)

MATCH_MOVIES = text(
    "select content "
    "from match_movies(:query_embedding, :match_threshold, :match_count)"
).bindparams(bindparam("query_embedding", type_=Vector(1536)))

class MovieRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_embedding(
        self, content: str, embedding: list[float]
    ) -> Movie:
        movie = Movie(content=content, embedding=embedding)
        self._session.add(movie)
        await self._session.flush()
        
        return movie

    async def create_embeddings(
        self, chunks: list[str], embeddings: list[list[float]]
    ) -> list[Movie]:
        movies = [
            Movie(content=content, embedding=embedding)
            for content, embedding in zip(chunks, embeddings, strict=True)
        ]
        self._session.add_all(movies)
        await self._session.flush()
        
        return movies

    async def find_similar_movies(self, embedding: list[float]) -> list[str]:
        result = await self._session.execute(
            MATCH_MOVIES,
            {
                "query_embedding": embedding,
                "match_threshold": 0.72,
                "match_count": 8,
            },
        )
        return list(result.scalars())
