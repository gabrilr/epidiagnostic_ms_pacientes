"""
Caso de uso: ListarCatalogoOffline

TODO: Implementar el endpoint GET /pacientes/catalogo?desde=...&comunidad=...

Debe:
1. Recibir un timestamp `desde` y un filtro opcional `comunidad`.
2. Llamar a paciente_repository.listar_actualizados_desde(desde, comunidad).
3. Mapear cada Paciente a PacienteOutputDTO (reutilizar el método
   estático _a_dto de CrearPacienteUseCase, o extraerlo a un mapper
   compartido en app/application/mappers/paciente_mapper.py para no
   duplicar la lógica de mapeo entre casos de uso).
4. Este es el caso de uso que la app móvil offline-first llama cada vez
   que tiene señal, para mantener actualizado su catálogo local de
   pacientes (según la decisión de diseño confirmada: "el celular
   deberá actualizar su información... teniendo un catálogo offline
   actualizado cada que le sea posible").

Ejemplo de firma esperada:

    class ListarCatalogoOfflineUseCase:
        def __init__(self, paciente_repository: PacienteRepository):
            self._paciente_repository = paciente_repository

        async def ejecutar(
            self, desde: datetime, comunidad: str | None = None
        ) -> list[PacienteOutputDTO]:
            pacientes = await self._paciente_repository.listar_actualizados_desde(desde, comunidad)
            return [self._a_dto(p) for p in pacientes]
"""
