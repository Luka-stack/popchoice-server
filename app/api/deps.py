from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.core.config import settings
from app.agent.runtime import AgentRuntime
from app.services.movie_service import MovieService
from app.services.group_strategy import GroupStrategy
from app.respositories.movie_repository import MovieRepository

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_agent_runtime(request: Request) -> AgentRuntime:
    return request.app.state.agent

AgentRuntimeDep = Annotated[AgentRuntime, Depends(get_agent_runtime)]


def get_movie_repository(session: SessionDep) -> MovieRepository:
    return MovieRepository(session)

MovieRepositoryDep = Annotated[MovieRepository, Depends(get_movie_repository)]


def get_movie_service(repo: MovieRepositoryDep, agent: AgentRuntimeDep) -> MovieService:
    return MovieService(
        repo, 
        agent,
        strategy=GroupStrategy(settings.group_strategy),
        mixed_penalty=settings.group_mixed_penalty,
        candidate_count=settings.group_candidate_count,
    )

MovieServiceDep = Annotated[MovieService, Depends(get_movie_service)]
