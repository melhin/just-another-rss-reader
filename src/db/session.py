from contextlib import asynccontextmanager
from typing import AsyncGenerator
from asyncio import current_task

from sqlalchemy.orm import sessionmaker
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_scoped_session

from src.settings import settings


def make_engine() -> AsyncEngine:
    """This function creates SQLAlchemy engine instance.

    :return: async engine
    """
    return create_async_engine(str(settings.db_url), echo=settings.db_echo, **settings.ssl_params)


def make_session_factory(engine: AsyncEngine) -> async_scoped_session:
    """Create session_factory for creating sessions.

    :param engine: async engine
    :return: session factory
    """
    return async_scoped_session(
        sessionmaker(
            engine,
            expire_on_commit=False,
            class_=AsyncSession,
        ),
        scopefunc=current_task,
    )


@asynccontextmanager
async def get_db_session_from_request(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Create and get database session.
    :param request: current request.
    :yield: database session.
    """
    session: AsyncSession = request.app.state.db_session_factory()

    try:  # noqa: WPS501
        yield session
    finally:
        await session.commit()
        await session.close()


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create and get database session.
    :param request: current request.
    :yield: database session.
    """
    db_engine = make_engine()
    db_session_factory = make_session_factory(db_engine)
    session: AsyncSession = db_session_factory()

    try:  # noqa: WPS501
        yield session
    finally:
        await session.commit()
        await session.close()
