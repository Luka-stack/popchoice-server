import logging

from app.respositories.movie_repository import MovieRepository
from app.schemas.movie import MovieCreate, MovieRecommendations, UserPreferences
from app.agent.runtime import AgentRuntime

logger = logging.getLogger(__name__)

RECOMMENDATION_EMBEDDING = """
    A {q3}, {q2} movie. Similar in spirit to {q1}. Featuring someone like {q4}
"""


class MovieService:
    def __init__(self, repo: MovieRepository, agent: AgentRuntime):
        self._repo = repo
        self._agent = agent

    async def create_embedding(self, movie: MovieCreate) -> None:
        content = f"{movie.title} ({movie.release_year}) | {movie.age_rating} | {movie.duration} | Rating: {movie.rating}:\n{movie.content}"
        embedding = await self._agent.create_embedding(content)
        await self._repo.create_embedding(content, embedding)

    async def recommend_movies(self, payload: UserPreferences) -> MovieRecommendations:
        embedding = await self._agent.create_embedding(
            RECOMMENDATION_EMBEDDING.format(
                q1=payload.preferences[0].q1,
                q2=payload.preferences[0].q2,
                q3=payload.preferences[0].q3,
                q4=payload.preferences[0].q4
            )
        )
        matching_movies = await self._repo.find_similar_movies(embedding)
        return await self._agent.recommend_movies(matching_movies, payload)
