import logging


from app.agent.runtime import AgentRuntime
from app.services.group_strategy import GroupStrategy, group_score
from app.respositories.movie_repository import MovieRepository
from app.schemas.movie import MovieCreate, MovieRecommendations, UserPreferences


logger = logging.getLogger(__name__)

RECOMMENDATION_EMBEDDING = """
    A {q3}, {q2} movie. Similar in spirit to {q1}. Featuring someone like {q4}
"""


class MovieService:
    def __init__(
        self, 
        repo: MovieRepository, 
        agent: AgentRuntime,
        strategy: GroupStrategy,
        mixed_penalty: float,
        candidate_count: int,
    ):
        self._repo = repo
        self._agent = agent
        self._strategy = strategy
        self._mixed_penalty = mixed_penalty
        self._candidate_count = candidate_count

    async def create_embedding(self, movie: MovieCreate) -> None:
        content = f"{movie.title} ({movie.release_year}) | {movie.age_rating} | {movie.duration} | Rating: {movie.rating}:\n{movie.content}"
        embedding = await self._agent.create_embedding(content)
        await self._repo.create_embedding(content, embedding)

    # async def recommend_movies(self, payload: UserPreferences) -> MovieRecommendations:
    #     embedding = await self._agent.create_embedding(
    #         RECOMMENDATION_EMBEDDING.format(
    #             q1=payload.preferences[0].q1,
    #             q2=payload.preferences[0].q2,
    #             q3=payload.preferences[0].q3,
    #             q4=payload.preferences[0].q4
    #         )
    #     )
    #     matching_movies = await self._repo.find_similar_movies(embedding)
    #     return await self._agent.recommend_movies(matching_movies, payload)

    async def recommend_movies_for_group(
        self, payload: UserPreferences
    ) -> MovieRecommendations:
        embeddings = await self._agent.create_embeddings([
            RECOMMENDATION_EMBEDDING.format(
                q1=p.q1,
                q2=p.q2,
                q3=p.q3,
                q4=p.q4
            )
            for p in payload.preferences
        ])
        scored_movies = await self._repo.score_movies_for_group(embeddings)

        ranked = sorted(
            scored_movies,
            key=lambda movie: group_score(movie[1], self._strategy, self._mixed_penalty),
            reverse=True
        )
        candidates = ranked[: max(self._candidate_count, payload.number_of_movies)]
        logger.info(
            "Group candidates (%s): %s",
            self._strategy,
            [(content.split(" (")[0], [round(s, 3) for s in sims]) for content, sims in candidates]
        )

        return await self._agent.recommend_movies(
            [content for content, _ in candidates], payload
        )
