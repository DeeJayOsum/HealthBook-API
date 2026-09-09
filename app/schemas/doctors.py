from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AvailabilitySlotCreate(BaseModel):
    starts_at: datetime
    ends_at: datetime


class AvailabilitySlotRead(AvailabilitySlotCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    doctor_id: int
    is_booked: bool


class DoctorProfileCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    specialisation: str = Field(min_length=1, max_length=150)


class DoctorRead(DoctorProfileCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int