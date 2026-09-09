from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment, AppointmentStatus
from app.models.availability import AvailabilitySlot
from app.models.patient import Patient
from app.models.user import User


async def book_appointment(
    session: AsyncSession, user: User, availability_slot_id: int
) -> Appointment:
    patient = await session.scalar(select(Patient).where(Patient.user_id == user.id))
    if patient is None:
        raise ValueError("Patient profile not found")
    slot = await session.scalar(
        select(AvailabilitySlot)
        .where(AvailabilitySlot.id == availability_slot_id)
        .with_for_update()
    )
    if slot is None:
        raise LookupError("Availability slot not found")
    if slot.is_booked:
        raise ValueError("Availability slot is already booked")
    slot.is_booked = True
    appointment = Appointment(
        patient_id=patient.id,
        availability_slot_id=slot.id,
        status=AppointmentStatus.PENDING,
    )
    session.add(appointment)
    await session.commit()
    await session.refresh(appointment)
    return appointment


async def list_patient_appointments(
    session: AsyncSession, user: User
) -> list[Appointment]:
    patient = await session.scalar(select(Patient).where(Patient.user_id == user.id))
    if patient is None:
        raise ValueError("Patient profile not found")
    result = await session.scalars(
        select(Appointment)
        .where(Appointment.patient_id == patient.id)
        .order_by(Appointment.id.desc())
    )
    return list(result)