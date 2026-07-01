"""
Tipo de columna GUID portable.

MySQL no tiene un tipo UUID nativo (a diferencia de PostgreSQL), así que
se almacena como CHAR(36) y se convierte automáticamente hacia/desde
`uuid.UUID` en cada lectura/escritura. Este es el patrón recomendado
oficialmente por SQLAlchemy para tipos portables entre dialectos:
https://docs.sqlalchemy.org/en/20/core/custom_types.html#backend-agnostic-guid-type

Usar este tipo en los modelos ORM en vez de un tipo específico de
dialecto evita tener que tocar los modelos si en el futuro se cambia
de motor de base de datos otra vez.
"""
import uuid

from sqlalchemy.types import CHAR, TypeDecorator


class GUID(TypeDecorator):
    impl = CHAR(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(uuid.UUID(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)
