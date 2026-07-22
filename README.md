# Microservicio 1 — Gestión de Pacientes

Parte de **EpiDiagnostic-Maya**. Responsable del registro de pacientes
y su historial médico. Arquitectura hexagonal · Patrón Database per
service.

Personal médico, autenticación (JWT) y suscripciones (plan Premium) se
extrajeron a su propio microservicio, **ms-personal (MS3)**, para que
cada servicio tenga una sola responsabilidad clara.

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

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| POST | `/pacientes` | Alta individual. Idempotente por CURP. | 🔒 |
| GET | `/pacientes/{id}` | Consulta puntual (usado por ms-atencion-medica). | 🔒 |
| POST | `/pacientes/sync` | Alta en batch desde la app móvil offline-first. | 🔒 |
| GET | `/pacientes/catalogo` | Descarga incremental del catálogo offline. | 🔒 |
| POST | `/pacientes/{id}/historial` | Anexa un antecedente médico (append-only). | 🔒 |
| PATCH | `/pacientes/{id}/datos` | Corrige datos básicos de un paciente existente. | 🔒 |
| GET | `/health` | Health check para orquestadores / API Gateway. | — |

🔒 = requiere `Authorization: Bearer <token>` — el token lo emite
**ms-personal (MS3)**, este microservicio solo lo verifica de forma
stateless con la misma llave compartida (`JWT_SECRET_KEY`/
`JWT_ALGORITHM`, deben coincidir exactamente).

## Regla de negocio clave: idempotencia silenciosa

Si llega un alta con un CURP que ya existe, el microservicio **no crea
un paciente nuevo ni lanza error**: devuelve el paciente existente con
`fue_creado_ahora: false`. Esto soporta el escenario de dos enfermeras
en distintas comunidades dando de alta al mismo paciente sin saberlo
estando ambas offline.

La corrección de datos de un paciente existente es un flujo **separado
y explícito** (`PATCH /pacientes/{id}/datos`), nunca inferido
automáticamente de un alta duplicada.

## Comunicación con otros microservicios

Este microservicio es consumido (no consume) por **ms-atencion-medica
(MS2)**, que llama a:

- `GET /pacientes/{id}` — validar que el paciente existe antes de registrar una atención
- `GET /pacientes/catalogo?desde=...` — la app móvil lo usa directamente para mantener su catálogo offline actualizado

La validación de `personal_id` (antes también resuelta aquí) ahora la
resuelve **ms-personal (MS3)** vía `GET /personal/{id}`.
