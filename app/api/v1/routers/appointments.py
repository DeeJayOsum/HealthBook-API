from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import DatabaseSession, require_role
from app.models.user import User
from app.schemas.appointments import AppointmentCreate, AppointmentRead
from app.services.appointments import book_appointment, list_patient_appointments

router = APIRouter(prefix="/appointments", tags=["appointments"])
PatientUser = Annotated[User, Depends(require_role("patient"))]


@router.post("", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    data: AppointmentCreate, session: DatabaseSession, user: PatientUser
):
    try:
        return await book_appointment(session, user, data.availability_slot_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("/mine", response_model=list[AppointmentRead])
async def get_my_appointments(session: DatabaseSession, user: PatientUser):
    return await list_patient_appointments(session, user)