import logging

from fastapi import APIRouter, status

from app.api.deps import AgentRuntimeDep, MovieRepositoryDep, MovieServiceDep
from app.schemas.movie import MovieCreate, MovieRecommendations, UserPreferences

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/movies", tags=["movies"])


@router.post("", response_model_exclude_none=True, status_code=status.HTTP_201_CREATED)
async def create_movie(payload: MovieCreate, service: MovieServiceDep):
    await service.create_embedding(payload)
    return {"message": "Movie created successfully"}

@router.post("/recommend", response_model=MovieRecommendations, status_code=status.HTTP_200_OK)
async def recommend_movies(payload: UserPreferences, service: MovieServiceDep):
    return await service.recommend_movies_for_group(payload)