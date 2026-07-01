"""
Configuración de base de datos: engine, sesión y Base declarativa.

Usa SQLAlchemy async con el driver aiomysql para MySQL, coherente
con FastAPI async end-to-end (evita bloquear el event loop con
operaciones de base de datos síncronas).
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.infrastructure.config.settings import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.db_echo,
    pool_pre_ping=True,  # importante en entornos con conexiones inestables/reinicios de red
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Clase base declarativa para todos los modelos ORM del microservicio."""
    pass


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency de FastAPI para inyectar una sesión de base de datos por
    request. Se usa con Depends(get_db_session) en los routers.
    """
    async with AsyncSessionLocal() as session:
        yield session
