from pydantic import BaseModel, ConfigDict


class AppointmentCreate(BaseModel):
    availability_slot_id: int


class AppointmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    availability_slot_id: int
    status: str