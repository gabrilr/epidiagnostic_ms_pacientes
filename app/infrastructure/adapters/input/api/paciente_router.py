"""
Adaptador de entrada: paciente_router

Expone los casos de uso de la capa de aplicación como endpoints HTTP.
Este router es DELGADO a propósito: no contiene lógica de negocio, solo
traduce HTTP <-> DTOs y delega todo al caso de uso correspondiente. Las
excepciones de dominio se traducen aquí a códigos HTTP apropiados.
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dtos.paciente_dto import (
    CrearPacienteInputDTO,
    SincronizarPacientesInputDTO,
)
from app.application.use_cases.consultar_paciente import ConsultarPacienteUseCase
from app.application.use_cases.crear_paciente import CrearPacienteUseCase
from app.application.use_cases.sincronizar_pacientes_batch import SincronizarPacientesBatchUseCase
from app.domain.exceptions.domain_exceptions import PacienteNoEncontradoException
from app.infrastructure.adapters.input.api.paciente_schemas import (
    CrearPacienteRequest,
    PacienteResponse,
    ResultadoSincronizacionResponse,
    SincronizarPacientesRequest,
    SincronizarPacientesResponse,
)
from app.infrastructure.dependency_injection import (
    get_consultar_paciente_use_case,
    get_crear_paciente_use_case,
    get_sincronizar_pacientes_batch_use_case,
)

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


@router.post(
    "",
    response_model=PacienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Da de alta un paciente. Idempotente por CURP.",
)
async def crear_paciente(
    request: CrearPacienteRequest,
    use_case: Annotated[CrearPacienteUseCase, Depends(get_crear_paciente_use_case)],
) -> PacienteResponse:
    """
    Si el CURP ya existe, NO se crea un paciente nuevo: se devuelve el
    existente con `fue_creado_ahora: false` (regla de negocio de
    idempotencia silenciosa, ver diseño de sincronización offline).
    """
    try:
        input_dto = CrearPacienteInputDTO(
            curp=request.curp,
            nombre_completo=request.nombre_completo,
            fecha_nacimiento=request.fecha_nacimiento,
            sexo=request.sexo,
            comunidad=request.comunidad,
            municipio=request.municipio,
            lengua_materna=request.lengua_materna,
            contacto_emergencia=request.contacto_emergencia,
            device_generated_id=request.device_generated_id,
        )
        resultado = await use_case.ejecutar(input_dto)
        return PacienteResponse(**resultado.__dict__)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error))


@router.get(
    "/{paciente_id}",
    response_model=PacienteResponse,
    summary="Consulta un paciente por ID. Usado por el microservicio de Atención Médica.",
)
async def consultar_paciente(
    paciente_id: UUID,
    use_case: Annotated[ConsultarPacienteUseCase, Depends(get_consultar_paciente_use_case)],
) -> PacienteResponse:
    try:
        resultado = await use_case.ejecutar(paciente_id)
        return PacienteResponse(**resultado.__dict__)
    except PacienteNoEncontradoException as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@router.post(
    "/sync",
    response_model=SincronizarPacientesResponse,
    summary="Sincronización batch de pacientes desde la app móvil offline-first.",
)
async def sincronizar_pacientes(
    request: SincronizarPacientesRequest,
    use_case: Annotated[
        SincronizarPacientesBatchUseCase, Depends(get_sincronizar_pacientes_batch_use_case)
    ],
) -> SincronizarPacientesResponse:
    """
    Procesa un lote de altas acumuladas en el celular durante periodos
    sin conectividad. Cada paciente del batch se procesa de forma
    independiente y tolerante a fallos: un error en uno no aborta el
    resto del batch (ver SincronizarPacientesBatchUseCase).
    """
    input_dto = SincronizarPacientesInputDTO(
        dispositivo_id=request.dispositivo_id,
        pacientes=[
            CrearPacienteInputDTO(
                curp=p.curp,
                nombre_completo=p.nombre_completo,
                fecha_nacimiento=p.fecha_nacimiento,
                sexo=p.sexo,
                comunidad=p.comunidad,
                municipio=p.municipio,
                lengua_materna=p.lengua_materna,
                contacto_emergencia=p.contacto_emergencia,
                device_generated_id=p.device_generated_id,
            )
            for p in request.pacientes
        ],
    )
    resultados = await use_case.ejecutar(input_dto)
    return SincronizarPacientesResponse(
        resultados=[ResultadoSincronizacionResponse(**r.__dict__) for r in resultados]
    )


# ---------------------------------------------------------------------
# TODO: Endpoints pendientes (ver casos de uso correspondientes, ya
# documentados con TODOs detallados en application/use_cases/):
#
# @router.get("/catalogo", ...)
#     -> usa ListarCatalogoOfflineUseCase (listar_catalogo_offline.py)
#     -> query params: desde (datetime), comunidad (str opcional)
#
# @router.post("/{paciente_id}/historial", ...)
#     -> usa AgregarAntecedenteHistorialUseCase (agregar_antecedente_historial.py)
#     -> requiere schema AgregarAntecedenteRequest en paciente_schemas.py
#
# @router.patch("/{paciente_id}/datos", ...)
#     -> usa ActualizarDatosPacienteUseCase (actualizar_datos_paciente.py)
#     -> requiere schema ActualizarDatosPacienteRequest en paciente_schemas.py
#     -> todos los campos del body deben ser opcionales (PATCH parcial)
# ---------------------------------------------------------------------
