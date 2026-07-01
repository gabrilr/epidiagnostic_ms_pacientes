"""
Entidad: HistorialMedico

Entidad interna del agregado Paciente. Un paciente puede o no tener
historial (lista vacía es un estado válido). La regla de negocio clave
es que el historial SIEMPRE se anexa, nunca se sobreescribe — un
antecedente, una vez registrado, no se borra ni se reemplaza
automáticamente (ver decisión de diseño sobre sincronización).
"""
from dataclasses import dataclass, field

from app.domain.entities.antecedente_medico import AntecedenteMedico


@dataclass
class HistorialMedico:
    antecedentes: list[AntecedenteMedico] = field(default_factory=list)

    def agregar_antecedente(self, antecedente: AntecedenteMedico) -> None:
        """
        Anexa un nuevo antecedente al historial. Nunca reemplaza ni
        elimina antecedentes existentes, en línea con la regla de
        negocio de que el historial es de solo-anexado (append-only).
        """
        self.antecedentes.append(antecedente)

    def esta_vacio(self) -> bool:
        return len(self.antecedentes) == 0
