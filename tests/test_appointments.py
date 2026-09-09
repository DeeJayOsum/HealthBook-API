from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient

from app.core.security import hash_password
from app.models.availability import AvailabilitySlot
from app.models.doctor import Doctor
from app.models.user import User, UserRole
from tests.database import session_factory


@pytest.mark.asyncio
async def test_patient_can_book_available_slot_once(client: AsyncClient):
    async with session_factory() as session:
        doctor_user = User(
            email="doctor@example.com",
            hashed_password=hash_password("strong-password"),
            role=UserRole.DOCTOR,
        )
        session.add(doctor_user)
        await session.flush()
        doctor = Doctor(
            user_id=doctor_user.id,
            first_name="Ada",
            last_name="Lovelace",
            specialisation="Cardiology",
        )
        session.add(doctor)
        await session.flush()
        slot = AvailabilitySlot(
            doctor_id=doctor.id,
            starts_at=datetime.now(UTC) + timedelta(days=1),
            ends_at=datetime.now(UTC) + timedelta(days=1, minutes=30),
        )
        session.add(slot)
        await session.commit()
        slot_id = slot.id

    registration = await client.post(
        "/api/v1/auth/register",
        json={"email": "patient@example.com", "password": "strong-password"},
    )
    assert registration.status_code == 201
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "patient@example.com", "password": "strong-password"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    available = await client.get("/api/v1/doctors/availability-slots")
    assert available.status_code == 200
    assert available.json()[0]["id"] == slot_id

    booking = await client.post(
        "/api/v1/appointments", json={"availability_slot_id": slot_id}, headers=headers
    )
    assert booking.status_code == 201
    assert booking.json()["status"] == "pending"

    duplicate = await client.post(
        "/api/v1/appointments", json={"availability_slot_id": slot_id}, headers=headers
    )
    assert duplicate.status_code == 409