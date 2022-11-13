from contextlib import asynccontextmanager
from typing import AsyncGenerator
from asyncio import current_task

from sqlalchemy.orm import sessionmaker
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_scoped_session

from config import settings


def make_engine(db_url: str) -> AsyncEngine:
    """This function creates SQLAlchemy engine instance.

    :return: async engine
    """
    return create_async_engine(
        db_url,
        echo=settings.db_echo,
        **settings.ssl_params,
        pool_size=5,
        pool_recycle=300,
        pool_pre_ping=True,
    )

async def make_session_factory(engine: AsyncEngine) -> async_scoped_session:
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
    session: AsyncSession = await make_session_factory(request.app.state.db_engine)

    try:  # noqa: WPS501
        yield session
    finally:
        await session.commit()
        await session.close()


@asynccontextmanager
async def get_db_session(db_url: str=str(settings.db_url)) -> AsyncGenerator[AsyncSession, None]:
    """
    Create and get database session.
    :param request: current request.
    :yield: database session.
    """
    db_engine = make_engine(db_url=db_url)
    session: AsyncSession = await make_session_factory(db_engine)

    try:  # noqa: WPS501
        yield session
    finally:
        await session.commit()
        await session.close()
