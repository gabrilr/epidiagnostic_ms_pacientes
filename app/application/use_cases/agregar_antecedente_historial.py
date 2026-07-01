"""
Caso de uso: AgregarAntecedenteHistorial

TODO: Implementar el endpoint POST /pacientes/{id}/historial

Debe:
1. Recibir paciente_id, descripcion, tipo (TipoAntecedente), y
   opcionalmente origen_atencion_id (cuando lo llama el microservicio 2
   tras registrar una atención que generó un diagnóstico crónico, por
   ejemplo).
2. Buscar el paciente con paciente_repository.buscar_por_id(). Si no
   existe, lanzar PacienteNoEncontradoException.
3. Crear una instancia de AntecedenteMedico.
4. Llamar a paciente.agregar_antecedente(antecedente) — NUNCA manipular
   el historial directamente, siempre a través del método de la raíz
   del agregado, para respetar el encapsulamiento.
5. Persistir con paciente_repository.actualizar(paciente).

Importante: este endpoint siempre AÑADE, nunca reemplaza ni elimina
antecedentes existentes (regla de negocio confirmada: el historial es
append-only).
"""
