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

SCORE_MOVIES_FOR_GROUP = text(
    """
    select m.content,
           array_agg(1 - (m.embedding <=> cast(q.embedding as vector)) order by q.position)
            as similarities
    from movies m
    cross join unnest(cast(:embeddings as text[])) with ordinality as q(embedding, position)
    where m.embedding is not null
    group by m.id, m.content
    """
)

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
    
    async def score_movies_for_group(
        self, embeddings: list[list[float]]
    ) -> list[tuple[str, list[float]]]:
        result = await self._session.execute(
            SCORE_MOVIES_FOR_GROUP,
            {
                "embeddings": [str(e) for e in embeddings]
            }
        )

        return [(row.content, row.similarities) for row in result]
