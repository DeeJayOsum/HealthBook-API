# HealthBook-API

Healthcare Appointment Booking System

Async FastAPI backend for a healthcare appointment booking portfolio project.

## Local development

1. Copy `.env.example` to `.env`.
2. Start PostgreSQL with `docker compose up -d db`.
3. Install dependencies with `poetry install`.
4. Run migrations with `poetry run alembic upgrade head`.
5. Start the API with `poetry run uvicorn app.main:app --reload`.

The API documentation is available at `http://localhost:8000/docs`.

## Main API flows

- `POST /api/v1/auth/register` creates a patient account and profile.
- `POST /api/v1/auth/register-doctor` creates a doctor account and profile.
- `POST /api/v1/auth/login` returns an access token and refresh token.
- `POST /api/v1/doctors/availability-slots` lets doctors publish slots.
- `GET /api/v1/doctors/availability-slots` lists unbooked slots.
- `POST /api/v1/appointments` lets patients book a slot once.
- `GET /api/v1/appointments/mine` lists the authenticated patient's appointments.

The appointment booking service locks the selected slot in the database before
marking it booked, protecting against competing booking requests.

## Checks

```text
poetry run ruff check .
poetry run black --check .
poetry run pytest
```
