"""
Excepciones de dominio.

Estas excepciones representan violaciones de reglas de negocio, NO errores
de infraestructura (esos se manejan en la capa de infraestructura). Los
adaptadores de entrada (API REST) son responsables de traducir estas
excepciones a códigos HTTP apropiados.
"""


class DomainException(Exception):
    """Excepción base para todas las excepciones de dominio."""
    pass


class PacienteYaExisteException(DomainException):
    """
    Se lanza cuando se intenta dar de alta un paciente cuyo CURP ya está
    registrado. Según la regla de negocio definida, este caso NO es un
    error fatal del sistema: se maneja de forma silenciosa devolviendo
    el paciente existente (ver CrearPacienteUseCase). Esta excepción se
    usa internamente en el repositorio/servicio de dominio para señalar
    la condición, pero el caso de uso la captura y la convierte en un
    resultado normal, no en un error propagado al cliente.
    """
    def __init__(self, curp: str):
        self.curp = curp
        super().__init__(f"Ya existe un paciente registrado con CURP {curp}.")


class PacienteNoEncontradoException(DomainException):
    """Se lanza cuando se busca un paciente por ID/CURP y no existe."""
    def __init__(self, identificador: str):
        self.identificador = identificador
        super().__init__(f"No se encontró ningún paciente con identificador {identificador}.")
