# Microservicio 1 — Gestión de Pacientes y Personal Médico

Parte de **EpiDiagnostic-Maya**. Responsable del registro de pacientes,
su historial médico, y registro de personal médico/enfermería.
Arquitectura hexagonal · Patrón Database per service.

## Estado de la implementación

Esto es un **esqueleto funcional**: la estructura hexagonal está
completa, y el flujo de **Pacientes** está implementado end-to-end
(dominio → aplicación → infraestructura → API). El módulo de
**Personal Médico** está documentado con TODOs detallados que siguen
exactamente el mismo patrón ya implementado, listos para completarse.

### Implementado y probado

- Entidades de dominio: `Paciente`, `HistorialMedico`, `AntecedenteMedico`, `PersonalMedico`
- Value Objects: `CURP` (con validación de formato), `Ubicacion`
- Puertos (interfaces): `PacienteRepository`, `PersonalRepository`
- Casos de uso: `CrearPacienteUseCase` (idempotente por CURP),
  `ConsultarPacienteUseCase`, `SincronizarPacientesBatchUseCase`
- Adaptador de persistencia: `PacienteRepositoryImpl` (SQLAlchemy async + MySQL)
- API REST: `POST /pacientes`, `GET /pacientes/{id}`, `POST /pacientes/sync`
- Inyección de dependencias completa
- Migraciones con Alembic (async)
- Tests unitarios de dominio (8 tests, sin necesidad de base de datos)

### Pendiente (TODOs documentados en el código)

- `PersonalModel` (modelo SQLAlchemy)
- `PersonalRepositoryImpl`
- `RegistrarPersonalUseCase`, `ConsultarPersonalUseCase`
- `personal_router.py`, `personal_schemas.py`
- `GET /pacientes/catalogo` (descarga incremental offline)
- `POST /pacientes/{id}/historial` (anexar antecedente)
- `PATCH /pacientes/{id}/datos` (corrección explícita de datos)

Cada uno de estos TODOs incluye, dentro del propio archivo, la firma de
métodos esperada y el patrón exacto a seguir (espejo de lo ya
implementado para Pacientes).

## Cómo levantar el proyecto

### Con Docker (recomendado)

```bash
cp .env.example .env
docker compose up --build
```

La API queda disponible en `http://localhost:8000`, con documentación
interactiva en `http://localhost:8000/docs`.

### Migraciones de base de datos

Con los contenedores corriendo:

```bash
docker compose exec api alembic revision --autogenerate -m "crear tablas iniciales"
docker compose exec api alembic upgrade head
```

### Correr tests unitarios (no requiere base de datos)

```bash
pip install -r requirements.txt
pytest tests/unit/ -v
```

## Endpoints implementados

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/pacientes` | Alta individual. Idempotente por CURP. |
| GET | `/pacientes/{id}` | Consulta puntual (usado por microservicio de Atención Médica). |
| POST | `/pacientes/sync` | Alta en batch desde la app móvil offline-first. |
| GET | `/health` | Health check para orquestadores / API Gateway. |

## Regla de negocio clave: idempotencia silenciosa

Si llega un alta con un CURP que ya existe, el microservicio **no crea
un paciente nuevo ni lanza error**: devuelve el paciente existente con
`fue_creado_ahora: false`. Esto soporta el escenario de dos enfermeras
en distintas comunidades dando de alta al mismo paciente sin saberlo
estando ambas offline.

La corrección de datos de un paciente existente es un flujo **separado
y explícito** (`PATCH /pacientes/{id}/datos`, pendiente de implementar),
nunca inferido automáticamente de un alta duplicada.

## Comunicación con otros microservicios

Este microservicio es consumido (no consume) por el microservicio de
**Atención Médica**, que llama a:

- `GET /pacientes/{id}` — validar que el paciente existe antes de registrar una atención
- `GET /personal/{id}` — validar que el personal médico existe y está activo
- `GET /pacientes/catalogo?desde=...` — la app móvil lo usa directamente para mantener su catálogo offline actualizado
