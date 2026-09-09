# GitHub Copilot Instructions — Healthcare Appointment Booking System

## Project Overview

This is a **Healthcare Appointment Booking System** — a portfolio project demonstrating
cloud-native backend development, built to complement prior enterprise Java/Spring Boot
experience with a modern Python stack.

**Goal:** Show clean API design, containerisation, and CI/CD — not just CRUD.

## Tech Stack

- **Language:** Python 3.12
- **Framework:** FastAPI (async, type-hinted)
- **Database:** PostgreSQL (via SQLAlchemy 2.0 async ORM + Alembic for migrations)
- **Auth:** JWT (via `python-jose` or `pyjwt`), OAuth2 password flow
- **Validation:** Pydantic v2 models for all request/response schemas
- **Testing:** pytest + httpx AsyncClient + pytest-asyncio
- **Containerisation:** Docker + docker-compose (app + Postgres)
- **CI/CD:** GitHub Actions → build → test → push to ECR → deploy to AWS App Runner
- **Package management:** Poetry (preferred) or requirements.txt with pip-tools

## Domain Model (core entities)

- `User` — base auth entity, has `role` enum: `patient`, `doctor`, `admin`
- `Patient` — profile linked to User
- `Doctor` — profile linked to User, has specialisation, has many `AvailabilitySlot`
- `AvailabilitySlot` — belongs to Doctor, has start/end time, `is_booked` flag
- `Appointment` — links Patient + AvailabilitySlot, has status enum:
  `pending`, `confirmed`, `cancelled`, `completed`

## Coding Conventions

### General

- Use **type hints everywhere** — function signatures, variables where non-obvious
- Use **async/await** consistently — this is an async FastAPI app, don't mix in
  blocking sync DB calls
- Follow **PEP 8**; format with `black`, lint with `ruff`
- Prefer **explicit over clever** — this code should be portfolio-readable, not golfed

### FastAPI structure

Follow this layout — don't collapse everything into `main.py`:

```
app/
  main.py              # app instantiation, router includes, startup/shutdown
  core/
    config.py          # Pydantic Settings, env vars
    security.py        # JWT creation/verification, password hashing
  api/
    deps.py            # shared dependencies (get_db, get_current_user, role guards)
    v1/
      routers/
        auth.py
        patients.py
        doctors.py
        appointments.py
  models/              # SQLAlchemy ORM models
  schemas/             # Pydantic request/response models — never reuse ORM models as schemas
  services/            # business logic, kept OUT of route handlers
  db/
    session.py         # async engine + session factory
    base.py

tests/
  conftest.py
  test_auth.py
  test_appointments.py
```

### Route handlers should be thin

Route functions parse input, call a service function, return output. **Business logic
lives in `services/`, not in the router.** When suggesting a new endpoint, always
propose the service-layer function alongside it.

### Pydantic schemas

- Always define separate `Create`, `Update`, and `Read`/`Out` schemas — never expose
  the ORM model directly, and never accept a full model as input (avoid mass-assignment)
- Use `model_config = ConfigDict(from_attributes=True)` for ORM → schema conversion

### Auth & security

- Passwords hashed with `bcrypt` via `passlib` — never store plaintext, ever
- JWT access tokens short-lived (~30 min); include a refresh token flow
- Role-based guards as FastAPI dependencies, e.g. `require_role("doctor")` —
  don't inline role checks inside route bodies
- Never log tokens, passwords, or PII (this is a healthcare-flavoured app —
  treat patient data as sensitive even though it's synthetic/demo data)

### Database

- All migrations go through **Alembic** — never suggest manual schema edits
- Use SQLAlchemy 2.0 style (`select()`, not legacy `Query` API)
- Foreign keys and relationships should be explicit; avoid raw SQL unless
  there's a clear performance reason (and comment why)

### Testing

- Every new endpoint needs at least: one happy-path test, one auth-failure test,
  one validation-failure test
- Use fixtures for test DB setup/teardown (a separate test Postgres DB or SQLite
  in-memory for speed, but flag if behaviour would differ from Postgres)
- Aim for tests to be runnable via `pytest` with zero manual setup beyond
  `docker-compose up -d db`

### Docker

- Multi-stage Dockerfile: build stage installs deps, final stage is slim
  (`python:3.12-slim`) with only runtime deps
- `docker-compose.yml` should spin up `api` + `db` with healthchecks, so
  `docker-compose up` alone gets a working local environment
- Never bake secrets into the image — use env vars / `.env` (git-ignored)

### CI/CD (GitHub Actions)

When asked to scaffold workflows, follow this pipeline order:

1. Checkout → set up Python → install deps (cached)
2. Lint (`ruff`) + format check (`black --check`)
3. Run tests (`pytest`) against a Postgres service container
4. Build Docker image
5. Push to Amazon ECR (only on `main` branch merges)
6. Deploy to AWS App Runner (only on `main`)

### Naming

- snake_case for Python variables/functions, PascalCase for classes
- Table names plural snake_case (`appointments`, `availability_slots`)
- Route paths kebab-case where multi-word (`/availability-slots`)

## What NOT to suggest

- Don't suggest Flask/Django patterns — this is FastAPI, keep it async-native
- Don't suggest storing JWT secrets or DB credentials in code — always env vars
- Don't suggest synchronous `psycopg2` — use `asyncpg` via SQLAlchemy async engine
- Don't over-engineer with unnecessary design patterns — this is a portfolio
  project; prioritise readability and correctness over abstraction depth
- Don't reuse ORM models as API response models — always go through Pydantic schemas

## Current Priorities (update as project progresses)

- [x] Phase 1: Core models + auth (JWT, register/login)
- [x] Phase 2: Doctor availability + patient booking endpoints
- [x] Phase 3: Dockerize + docker-compose local setup
- [x] Phase 4: GitHub Actions CI (lint/test/build)
- [ ] Phase 5: AWS deployment (ECR + App Runner) + CD
- [ ] Phase 6: README + architecture diagram for portfolio presentation
