"""
Caso de uso: SincronizarPacientesBatch

Implementa el endpoint POST /pacientes/sync, usado por la app móvil
offline-first cuando recupera conectividad y necesita subir todas las
altas acumuladas localmente.

Reutiliza CrearPacienteUseCase para cada paciente del batch, de modo
que la regla de idempotencia por CURP se aplica de forma consistente
sin duplicar lógica.

Nota de diseño: se procesa el batch de forma secuencial y tolerante a
fallos individuales — si un paciente del batch tiene datos inválidos
(ej. CURP mal formado), no se aborta todo el batch; ese paciente se
reporta con error y los demás se procesan normalmente. Esto es
importante en un contexto de conectividad limitada: el celular no debe
tener que reintentar el batch completo por un solo registro problemático.
"""
from app.application.dtos.paciente_dto import (
    ResultadoSincronizacionDTO,
    SincronizarPacientesInputDTO,
)
from app.application.use_cases.crear_paciente import CrearPacienteUseCase


class SincronizarPacientesBatchUseCase:

    def __init__(self, crear_paciente_use_case: CrearPacienteUseCase):
        self._crear_paciente_use_case = crear_paciente_use_case

    async def ejecutar(
        self, datos: SincronizarPacientesInputDTO
    ) -> list[ResultadoSincronizacionDTO]:
        resultados: list[ResultadoSincronizacionDTO] = []

        for paciente_input in datos.pacientes:
            try:
                resultado = await self._crear_paciente_use_case.ejecutar(paciente_input)
                resultados.append(
                    ResultadoSincronizacionDTO(
                        device_generated_id=paciente_input.device_generated_id,
                        id_servidor=resultado.id,
                        curp=resultado.curp,
                        estado="creado" if resultado.fue_creado_ahora else "ya_existente",
                    )
                )
            except ValueError as error:
                # TODO: registrar el error en un log estructurado y/o en
                # una tabla de "registros con error de sincronización"
                # para que el equipo pueda darle seguimiento manual.
                resultados.append(
                    ResultadoSincronizacionDTO(
                        device_generated_id=paciente_input.device_generated_id,
                        id_servidor="",
                        curp=paciente_input.curp,
                        estado=f"error: {str(error)}",
                    )
                )

        return resultados
