"""
Configuración de base de datos: engine, sesión y Base declarativa.

Usa SQLAlchemy async con el driver aiomysql para MySQL, coherente
con FastAPI async end-to-end (evita bloquear el event loop con
operaciones de base de datos síncronas).
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# Parche de compatibilidad para evitar TypeError en pool_pre_ping con PyMySQL >= 1.2.0 y aiomysql.
# PyMySQL >= 1.2.0 cambia la firma/valor predeterminado de ping(), provocando que SQLAlchemy
# llame a ping() sin argumentos, lo cual falla en el adaptador de aiomysql.
try:
    from sqlalchemy.dialects.mysql.aiomysql import AsyncAdapt_aiomysql_connection
    _original_ping = AsyncAdapt_aiomysql_connection.ping
    def _patched_ping(self, reconnect=True):
        return _original_ping(self, reconnect)
    AsyncAdapt_aiomysql_connection.ping = _patched_ping
except ImportError:
    pass

from app.infrastructure.config.settings import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.db_echo,
    pool_pre_ping=True,
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
