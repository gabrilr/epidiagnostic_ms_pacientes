"""
Adaptador de entrada: paciente_router

Expone los casos de uso de la capa de aplicación como endpoints HTTP.
Este router es DELGADO a propósito: no contiene lógica de negocio, solo
traduce HTTP <-> DTOs y delega todo al caso de uso correspondiente. Las
excepciones de dominio se traducen aquí a códigos HTTP apropiados.
"""
from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.dtos.paciente_dto import (
    ActualizarDatosPacienteInputDTO,
    AgregarAntecedenteInputDTO,
    CrearPacienteInputDTO,
    SincronizarPacientesInputDTO,
)
from app.application.use_cases.actualizar_datos_paciente import ActualizarDatosPacienteUseCase
from app.application.use_cases.agregar_antecedente_historial import AgregarAntecedenteHistorialUseCase
from app.application.use_cases.consultar_paciente import ConsultarPacienteUseCase
from app.application.use_cases.crear_paciente import CrearPacienteUseCase
from app.application.use_cases.listar_catalogo_offline import ListarCatalogoOfflineUseCase
from app.application.use_cases.sincronizar_pacientes_batch import SincronizarPacientesBatchUseCase
from app.domain.exceptions.domain_exceptions import PacienteNoEncontradoException
from app.infrastructure.adapters.input.api.paciente_schemas import (
    ActualizarDatosPacienteRequest,
    AgregarAntecedenteRequest,
    CrearPacienteRequest,
    PacienteResponse,
    ResultadoSincronizacionResponse,
    SincronizarPacientesRequest,
    SincronizarPacientesResponse,
)
from app.infrastructure.adapters.input.api.auth_dependencies import get_personal_id_actual
from app.infrastructure.dependency_injection import (
    get_actualizar_datos_paciente_use_case,
    get_agregar_antecedente_historial_use_case,
    get_consultar_paciente_use_case,
    get_crear_paciente_use_case,
    get_listar_catalogo_offline_use_case,
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
    _personal_id: Annotated[UUID, Depends(get_personal_id_actual)],
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
    "/catalogo",
    response_model=list[PacienteResponse],
    summary="Descarga incremental del catálogo offline para la app móvil.",
)
async def listar_catalogo_offline(
    use_case: Annotated[ListarCatalogoOfflineUseCase, Depends(get_listar_catalogo_offline_use_case)],
    _personal_id: Annotated[UUID, Depends(get_personal_id_actual)],
    desde: datetime | None = Query(
        default=None,
        description="Solo pacientes actualizados desde esta fecha. Si se omite, devuelve el catálogo completo.",
    ),
    comunidad: str | None = Query(default=None, description="Filtra por comunidad, para no sobrecargar el celular."),
) -> list[PacienteResponse]:
    """
    Sync incremental: la app móvil guarda localmente la fecha de su
    última descarga exitosa y la manda como `desde` la próxima vez, en
    vez de traer el catálogo completo en cada llamada.
    """
    resultados = await use_case.ejecutar(desde=desde, comunidad=comunidad)
    return [PacienteResponse(**r.__dict__) for r in resultados]


# NOTA: esta ruta debe ir DESPUÉS de "/catalogo" — ambas son de un solo
# segmento bajo /pacientes, y FastAPI resuelve por orden de registro. Si
# "/{paciente_id}" se registrara primero, "/pacientes/catalogo" caería
# en este handler (con "catalogo" como paciente_id) y fallaría al
# convertir a UUID en vez de llegar al handler correcto.
@router.get(
    "/{paciente_id}",
    response_model=PacienteResponse,
    summary="Consulta un paciente por ID. Usado por el microservicio de Atención Médica.",
)
async def consultar_paciente(
    paciente_id: UUID,
    use_case: Annotated[ConsultarPacienteUseCase, Depends(get_consultar_paciente_use_case)],
    _personal_id: Annotated[UUID, Depends(get_personal_id_actual)],
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
    _personal_id: Annotated[UUID, Depends(get_personal_id_actual)],
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


@router.post(
    "/{paciente_id}/historial",
    response_model=PacienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Anexa un antecedente médico al historial del paciente.",
)
async def agregar_antecedente_historial(
    paciente_id: UUID,
    request: AgregarAntecedenteRequest,
    use_case: Annotated[
        AgregarAntecedenteHistorialUseCase, Depends(get_agregar_antecedente_historial_use_case)
    ],
    _personal_id: Annotated[UUID, Depends(get_personal_id_actual)],
) -> PacienteResponse:
    """
    El historial es append-only: este endpoint siempre AÑADE un
    antecedente nuevo, nunca reemplaza ni elimina los existentes.
    """
    try:
        input_dto = AgregarAntecedenteInputDTO(
            descripcion=request.descripcion,
            tipo=request.tipo,
            origen_atencion_id=request.origen_atencion_id,
        )
        resultado = await use_case.ejecutar(paciente_id, input_dto)
        return PacienteResponse(**resultado.__dict__)
    except PacienteNoEncontradoException as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error))


@router.patch(
    "/{paciente_id}/datos",
    response_model=PacienteResponse,
    summary="Corrige datos básicos de un paciente existente.",
)
async def actualizar_datos_paciente(
    paciente_id: UUID,
    request: ActualizarDatosPacienteRequest,
    use_case: Annotated[ActualizarDatosPacienteUseCase, Depends(get_actualizar_datos_paciente_use_case)],
    _personal_id: Annotated[UUID, Depends(get_personal_id_actual)],
) -> PacienteResponse:
    """
    Única vía para corregir datos de un paciente ya registrado. Nunca se
    infiere de un alta duplicada (ver CrearPacienteUseCase): debe ser
    una acción explícita del personal médico que detecta el dato
    desactualizado. PATCH parcial: solo se actualiza lo que venga en el
    body distinto de null.
    """
    try:
        input_dto = ActualizarDatosPacienteInputDTO(
            nombre_completo=request.nombre_completo,
            comunidad=request.comunidad,
            municipio=request.municipio,
            lengua_materna=request.lengua_materna,
            contacto_emergencia=request.contacto_emergencia,
        )
        resultado = await use_case.ejecutar(paciente_id, input_dto)
        return PacienteResponse(**resultado.__dict__)
    except PacienteNoEncontradoException as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error))
