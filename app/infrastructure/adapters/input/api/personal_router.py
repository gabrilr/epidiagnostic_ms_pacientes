"""
Adaptador de entrada: personal_router

Endpoints de registro y consulta de personal médico.
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dtos.personal_dto import RegistrarPersonalInputDTO
from app.application.use_cases.registrar_personal import (
    ConsultarPersonalUseCase,
    RegistrarPersonalUseCase,
)
from app.domain.exceptions.domain_exceptions import PersonalNoEncontradoException
from app.infrastructure.adapters.input.api.personal_schemas import (
    PersonalResponse,
    RegistrarPersonalRequest,
)
from app.infrastructure.dependency_injection import (
    get_consultar_personal_use_case,
    get_registrar_personal_use_case,
)

router = APIRouter(prefix="/personal", tags=["Personal Médico"])


@router.post(
    "",
    response_model=PersonalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registra un médico o enfermera.",
)
async def registrar_personal(
    request: RegistrarPersonalRequest,
    use_case: Annotated[RegistrarPersonalUseCase, Depends(get_registrar_personal_use_case)],
) -> PersonalResponse:
    try:
        input_dto = RegistrarPersonalInputDTO(
            nombre_completo=request.nombre_completo,
            tipo=request.tipo,
            comunidad=request.comunidad,
            municipio=request.municipio,
            cedula_profesional=request.cedula_profesional,
        )
        resultado = await use_case.ejecutar(input_dto)
        return PersonalResponse(**resultado.__dict__)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error))


@router.get(
    "/{personal_id}",
    response_model=PersonalResponse,
    summary="Consulta personal médico por ID. Usado por el Microservicio de Atención Médica.",
)
async def consultar_personal(
    personal_id: UUID,
    use_case: Annotated[ConsultarPersonalUseCase, Depends(get_consultar_personal_use_case)],
) -> PersonalResponse:
    try:
        resultado = await use_case.ejecutar(personal_id)
        return PersonalResponse(**resultado.__dict__)
    except PersonalNoEncontradoException as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
