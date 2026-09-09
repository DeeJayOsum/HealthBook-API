from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import DatabaseSession, require_role
from app.models.user import User
from app.schemas.doctors import (
    AvailabilitySlotCreate,
    AvailabilitySlotRead,
    DoctorProfileCreate,
    DoctorRead,
)
from app.services.doctors import (
    create_availability_slot,
    create_doctor_profile,
    list_available_slots,
)

router = APIRouter(prefix="/doctors", tags=["doctors"])
DoctorUser = Annotated[User, Depends(require_role("doctor"))]


@router.post("/profile", response_model=DoctorRead, status_code=status.HTTP_201_CREATED)
async def create_profile(
    data: DoctorProfileCreate, session: DatabaseSession, user: DoctorUser
)-> DoctorRead:
    try:
        return await create_doctor_profile(session, user, data)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.post("/availability-slots", response_model=AvailabilitySlotRead)
async def create_slot(
    data: AvailabilitySlotCreate, session: DatabaseSession, user: DoctorUser
):
    try:
        return await create_availability_slot(session, user, data)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/availability-slots", response_model=list[AvailabilitySlotRead])
async def get_available_slots(session: DatabaseSession):
    return await list_available_slots(session)