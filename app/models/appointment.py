from enum import StrEnum

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AppointmentStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    availability_slot_id: Mapped[int] = mapped_column(
        ForeignKey("availability_slots.id"), unique=True
    )
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(
            AppointmentStatus,
            name="appointment_status",
            values_callable=lambda enum_type: [member.value for member in enum_type],
        ),
        default=AppointmentStatus.PENDING,
    )

    patient = relationship("Patient")
    availability_slot = relationship("AvailabilitySlot")