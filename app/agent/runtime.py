import logging

from openai import AsyncOpenAI

from app.core.config import Settings
from app.schemas.movie import MovieRecommendations, UserPreferences
from app.agent.prompts import SYSTEM_PROMPT, MEMBER_PREFERENCES_TEMPLATE, GROUP_PREFERENCES_TEMPLATE

logger = logging.getLogger(__name__)


class AgentRuntime:
    def __init__(
        self, 
        openai: AsyncOpenAI, 
        openai_embedding_model: str, 
        openai_recommendation_model: str
    ) -> None:
        self.openai = openai
        self.openai_embedding_model = openai_embedding_model
        self.openai_recommendation_model = openai_recommendation_model

    @classmethod
    async def create(cls, settings: Settings) -> "AgentRuntime":
        if settings.openai_api_key is None:
            raise RuntimeError("OpenAI API key is not set")

        openai = AsyncOpenAI(api_key=settings.openai_api_key.get_secret_value())
        return cls(
            openai=openai,
            openai_embedding_model=settings.openai_embedding_model,
            openai_recommendation_model=settings.openai_recommendation_model
        )

    async def create_embedding(self, content: str) -> list[float]:
        return (await self.create_embeddings([content]))[0]

    async def create_embeddings(self, contents: list[str]) -> list[list[float]]:
        response = await self.openai.embeddings.create(
            model=self.openai_embedding_model,
            input=contents
        )

        return [item.embedding for item in response.data]

    async def recommend_movies(
        self, 
        movies: list[str], 
        user_preferences: UserPreferences
    ) -> MovieRecommendations:
        recommendation_prompt = SYSTEM_PROMPT.format(
            context="\n".join(f"<MOVIE>{movie}</MOVIE>" for movie in movies)
        )
        members = "\n".join(
            MEMBER_PREFERENCES_TEMPLATE.format(
                name=p.name or f"Member {i}", q1=p.q1, q2=p.q2, q3=p.q3, q4=p.q4
            )
            for i, p in enumerate(user_preferences.preferences, start=1)
        )
        group_preferences = GROUP_PREFERENCES_TEMPLATE.format(
            number_of_movies=user_preferences.number_of_movies,
            members=members
        )

        response = await self.openai.chat.completions.parse(
            model=self.openai_recommendation_model,
            messages=[
                {
                    "role": "system",
                    "content": recommendation_prompt
                },
                {
                    "role": "user",
                    "content": group_preferences
                }
            ],
            temperature=0.5,
            response_format=MovieRecommendations,
        )

        message = response.choices[0].message
        if message.parsed is None:
            raise RuntimeError(f"Model did not return recommendations: {message.refusal}")

        return message.parsed