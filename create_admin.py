"""
Script para crear (o corregir a admin) un usuario administrador.

Uso:
    python create_admin.py --correo admin@epidiagnostix.mx \
        --nombre "Admin EpiDiagnostix" --contrasena "Admin2024!"

Si ya existe personal con ese correo, actualiza su tipo a 'admin' y su
contraseña a la indicada. Si no existe, lo crea. POST /personal no
acepta tipo='admin' (por seguridad, para que nadie se autoregistre
como admin vía la API pública): este script es la única vía.
"""
import argparse
import asyncio

from passlib.context import CryptContext
from sqlalchemy import select

from app.infrastructure.adapters.output.persistence.models.personal_model import PersonalModel
from app.infrastructure.config.database import AsyncSessionLocal

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def crear_o_corregir_admin(
    correo: str, nombre: str, contrasena: str, comunidad: str, municipio: str
) -> None:
    async with AsyncSessionLocal() as session:
        resultado = await session.execute(
            select(PersonalModel).where(PersonalModel.correo == correo)
        )
        modelo = resultado.scalar_one_or_none()
        contrasena_hash = pwd_context.hash(contrasena)

        if modelo is not None:
            modelo.tipo = "admin"
            modelo.nombre_completo = nombre
            modelo.contrasena_hash = contrasena_hash
            modelo.activo = True
            await session.commit()
            print(f"Usuario existente '{correo}' actualizado a tipo=admin.")
            return

        nuevo = PersonalModel(
            nombre_completo=nombre,
            tipo="admin",
            comunidad=comunidad,
            municipio=municipio,
            correo=correo,
            contrasena_hash=contrasena_hash,
        )
        session.add(nuevo)
        await session.commit()
        print(f"Usuario administrador '{correo}' creado.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Crea o corrige un usuario administrador.")
    parser.add_argument("--correo", required=True)
    parser.add_argument("--nombre", required=True)
    parser.add_argument("--contrasena", required=True)
    parser.add_argument("--comunidad", default="N/A", help="No aplica para cuentas admin.")
    parser.add_argument("--municipio", default="N/A", help="No aplica para cuentas admin.")
    args = parser.parse_args()

    asyncio.run(
        crear_o_corregir_admin(
            correo=args.correo,
            nombre=args.nombre,
            contrasena=args.contrasena,
            comunidad=args.comunidad,
            municipio=args.municipio,
        )
    )


if __name__ == "__main__":
    main()
