from pydantic import BaseModel, ConfigDict, Field
from typing import Literal, List

    
class _SchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")


class MovieCreate(_SchemaBase):
    title: str = Field(min_length=2)
    release_year: str = Field(min_length=4, max_length=4)
    age_rating: str = Field(min_length=1)
    duration: str = Field(min_length=1)
    rating: float = Field(gt=0, le=10)
    content: str = Field(min_length=10)


class Preference(_SchemaBase):
    q1: str = Field(min_length=1)
    q2: Literal["new", "classic"]
    q3: Literal["fun", "serious", "inspiring", "scary"]
    q4: str = Field(min_length=1)


class UserPreferences(_SchemaBase):
    number_of_movies: int = Field(gt=0)
    preferences: List[Preference]


class RecommendedMovie(_SchemaBase):
    title: str = Field(description="Exact movie title as written in MOVIE_CONTEXT")
    release_year: str = Field(description="Four-digit release year")
    short_description: str = Field(
        description="2-3 sentences, review-style, on why the movie fits the user's preferences"
    )


class MovieRecommendations(_SchemaBase):
    movies: List[RecommendedMovie]
