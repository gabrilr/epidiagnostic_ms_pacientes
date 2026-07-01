"""
Punto de entrada de la aplicación FastAPI.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.adapters.input.api.paciente_router import router as paciente_router
from app.infrastructure.adapters.input.api.personal_router import router as personal_router
from app.infrastructure.config.database import engine
from app.infrastructure.config.settings import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.connect() as connection:
        pass
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description=(
        "Microservicio de gestión de pacientes y personal médico para "
        "EpiDiagnostic-Maya. Responsable de registro de pacientes, su "
        "historial médico, y registro de personal médico/enfermería. "
        "Patrón: Database per service."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(paciente_router)
app.include_router(personal_router)


@app.get("/health", tags=["Sistema"], summary="Health check para orquestadores/API Gateway")
async def health_check() -> dict:
    return {"status": "ok", "service": settings.app_name, "environment": settings.environment}
