"""
Tests unitarios de la entidad Paciente y value objects.

Estos tests NO requieren base de datos ni FastAPI: validan solo el
dominio puro, que es justamente el beneficio de la arquitectura
hexagonal (el núcleo de negocio se puede probar de forma aislada).
"""
from datetime import date

# pyrefly: ignore [missing-import]
import pytest

from app.domain.entities.antecedente_medico import AntecedenteMedico, TipoAntecedente
from app.domain.entities.paciente import Paciente
from app.domain.value_objects.curp import CURP
from app.domain.value_objects.ubicacion import Ubicacion


def _crear_paciente_valido() -> Paciente:
    return Paciente(
        curp=CURP("GOMC900101HCSNZL09"),
        nombre_completo="Carlos Gómez Méndez",
        fecha_nacimiento=date(1990, 1, 1),
        sexo="H",
        ubicacion=Ubicacion(comunidad="Oxchuc", municipio="Oxchuc"),
        lengua_materna="Tseltal",
        contacto_emergencia="9611234567",
    )


def test_curp_valido_se_normaliza_a_mayusculas():
    curp = CURP("gomc900101hcsnzl09")
    assert curp.valor == "GOMC900101HCSNZL09"


def test_curp_invalido_lanza_excepcion():
    with pytest.raises(ValueError):
        CURP("INVALIDO123")


def test_ubicacion_vacia_lanza_excepcion():
    with pytest.raises(ValueError):
        Ubicacion(comunidad="", municipio="Oxchuc")


def test_crear_paciente_valido():
    paciente = _crear_paciente_valido()
    assert paciente.nombre_completo == "Carlos Gómez Méndez"
    assert paciente.historial.esta_vacio()


def test_paciente_con_sexo_invalido_lanza_excepcion():
    with pytest.raises(ValueError):
        Paciente(
            curp=CURP("GOMC900101HCSNZL09"),
            nombre_completo="Carlos Gómez Méndez",
            fecha_nacimiento=date(1990, 1, 1),
            sexo="X",  # inválido, debe ser H o M
            ubicacion=Ubicacion(comunidad="Oxchuc", municipio="Oxchuc"),
            lengua_materna=None,
            contacto_emergencia=None,
        )


def test_paciente_con_fecha_nacimiento_futura_lanza_excepcion():
    with pytest.raises(ValueError):
        Paciente(
            curp=CURP("GOMC900101HCSNZL09"),
            nombre_completo="Carlos Gómez Méndez",
            fecha_nacimiento=date(2099, 1, 1),
            sexo="H",
            ubicacion=Ubicacion(comunidad="Oxchuc", municipio="Oxchuc"),
            lengua_materna=None,
            contacto_emergencia=None,
        )


def test_paciente_con_contacto_emergencia_invalido_lanza_excepcion():
    with pytest.raises(ValueError):
        Paciente(
            curp=CURP("GOMC900101HCSNZL09"),
            nombre_completo="Carlos Gómez Méndez",
            fecha_nacimiento=date(1990, 1, 1),
            sexo="H",
            ubicacion=Ubicacion(comunidad="Oxchuc", municipio="Oxchuc"),
            lengua_materna=None,
            contacto_emergencia="12345",  # menor a 10
        )
    with pytest.raises(ValueError):
        Paciente(
            curp=CURP("GOMC900101HCSNZL09"),
            nombre_completo="Carlos Gómez Méndez",
            fecha_nacimiento=date(1990, 1, 1),
            sexo="H",
            ubicacion=Ubicacion(comunidad="Oxchuc", municipio="Oxchuc"),
            lengua_materna=None,
            contacto_emergencia="12345abcde",  # no numérico
        )


def test_agregar_antecedente_anexa_sin_reemplazar():
    paciente = _crear_paciente_valido()
    antecedente_1 = AntecedenteMedico(descripcion="Alergia a penicilina", tipo=TipoAntecedente.ALERGIA)
    antecedente_2 = AntecedenteMedico(descripcion="Diabetes tipo 2", tipo=TipoAntecedente.ENFERMEDAD_CRONICA)

    paciente.agregar_antecedente(antecedente_1)
    paciente.agregar_antecedente(antecedente_2)

    assert len(paciente.historial.antecedentes) == 2
    assert paciente.historial.antecedentes[0].descripcion == "Alergia a penicilina"
    assert paciente.historial.antecedentes[1].descripcion == "Diabetes tipo 2"


def test_actualizar_datos_basicos_solo_modifica_campos_provistos():
    paciente = _crear_paciente_valido()
    nombre_original = paciente.nombre_completo

    paciente.actualizar_datos_basicos(contacto_emergencia="9619999999")

    assert paciente.nombre_completo == nombre_original  # no se tocó
    assert paciente.contacto_emergencia == "9619999999"  # sí se actualizó
