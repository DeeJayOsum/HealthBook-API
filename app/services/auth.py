from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.user import User, UserRole
from app.schemas.auth import DoctorRegister, UserCreate


async def register_user(session: AsyncSession, data: UserCreate) -> User:
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        role=UserRole.PATIENT,
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ValueError("Email is already registered") from None
    await session.refresh(user)
    session.add(
        Patient(
            user_id=user.id,
            first_name=data.first_name,
            last_name=data.last_name,
        )
    )
    await session.commit()
    return user


async def authenticate_user(
    session: AsyncSession, email: str, password: str
) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user


async def register_doctor(session: AsyncSession, data: DoctorRegister) -> User:
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        role=UserRole.DOCTOR,
    )
    session.add(user)
    try:
        await session.flush()
        session.add(
            Doctor(
                user_id=user.id,
                first_name=data.first_name,
                last_name=data.last_name,
                specialisation=data.specialisation,
            )
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ValueError("Email is already registered") from None
    await session.refresh(user)
    return user