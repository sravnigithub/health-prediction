from sqlalchemy import Column, Integer, String, Float, Date
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    dob = Column(Date)
    email = Column(String, unique=True, index=True)
    glucose = Column(Float)
    haemoglobin = Column(Float)
    cholesterol = Column(Float)
    remarks = Column(String)

class PatientBase(BaseModel):
    full_name: str
    dob: date
    email: EmailStr
    glucose: float = Field(..., gt=0)
    haemoglobin: float = Field(..., gt=0)
    cholesterol: float = Field(..., gt=0)

    @field_validator('dob')
    @classmethod
    def validate_dob(cls, v):
        if v > date.today():
            raise ValueError('Date of birth cannot be in the future')
        return v

class PatientCreate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: int
    remarks: str

    class Config:
        from_attributes = True
