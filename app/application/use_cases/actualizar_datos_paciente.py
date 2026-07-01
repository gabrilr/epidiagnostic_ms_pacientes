"""
Caso de uso: ActualizarDatosPaciente

TODO: Implementar el endpoint PATCH /pacientes/{id}/datos

Debe:
1. Recibir paciente_id y los campos opcionales a actualizar (nombre,
   comunidad/municipio, lengua materna, contacto de emergencia).
2. Buscar el paciente. Si no existe, lanzar PacienteNoEncontradoException.
3. Llamar a paciente.actualizar_datos_basicos(...).
4. Persistir con paciente_repository.actualizar(paciente).

Importante (regla de negocio confirmada en el diseño): esta es la ÚNICA
vía para corregir datos de un paciente existente. La corrección NUNCA
debe inferirse automáticamente de un alta duplicada (CrearPacienteUseCase
ignora silenciosamente los duplicados sin fusionar datos) — debe ser
una acción explícita y consciente del personal médico que detecta el
dato desactualizado.
"""
