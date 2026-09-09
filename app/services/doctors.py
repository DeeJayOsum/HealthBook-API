from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.availability import AvailabilitySlot
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.doctors import AvailabilitySlotCreate, DoctorProfileCreate


async def create_doctor_profile(
    session: AsyncSession, user: User, data: DoctorProfileCreate
) -> Doctor:
    existing = await session.scalar(select(Doctor).where(Doctor.user_id == user.id))
    if existing is not None:
        raise ValueError("Doctor profile already exists")
    doctor = Doctor(user_id=user.id, **data.model_dump())
    session.add(doctor)
    await session.commit()
    await session.refresh(doctor)
    return doctor


async def create_availability_slot(
    session: AsyncSession, user: User, data: AvailabilitySlotCreate
) -> AvailabilitySlot:
    doctor = await session.scalar(select(Doctor).where(Doctor.user_id == user.id))
    if doctor is None:
        raise ValueError("Doctor profile not found")
    if data.ends_at <= data.starts_at:
        raise ValueError("Slot end time must be after start time")
    slot = AvailabilitySlot(doctor_id=doctor.id, **data.model_dump())
    session.add(slot)
    await session.commit()
    await session.refresh(slot)
    return slot


async def list_available_slots(session: AsyncSession) -> list[AvailabilitySlot]:
    result = await session.scalars(
        select(AvailabilitySlot)
        .where(AvailabilitySlot.is_booked.is_(False))
        .order_by(AvailabilitySlot.starts_at)
    )
    return list(result)