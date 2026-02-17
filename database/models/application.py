from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Index, DateTime, Enum, Date, Text
from sqlalchemy.orm import relationship, validates
from .base import Base
from .enums.application_status import ApplicationStatusEnum, GenderEnum, LevelEnum
import re



class Application(Base):
    __tablename__ = "application"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="applications") #relation with user

    #Status
    status = Column(Enum(ApplicationStatusEnum), nullable=False, index=True)

    #Personal Information
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)
    gender = Column(Enum(GenderEnum), nullable=True)


    #Contact Info
    address = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    email = Column(String, nullable=True)


    #Education skills and status
    is_student = Column(Boolean, default=True)
    education_place = Column(String, nullable=True)
    education_level = Column(String, nullable=True)

    #Additional education
    additional_courses = Column(String, nullable=True)
    additional_course_subject = Column(String, nullable=True)


    #maritial status
    marriage_status = Column(String, nullable=True, index=True)
    if_children = Column(String, nullable=True, index=True)

    #Language skills
    russian_level = Column(Enum(LevelEnum), nullable=True)
    russian_voice_path = Column(String(255), nullable=True)

    english_level = Column(Enum(LevelEnum), nullable=True)
    english_voice_path = Column(String(255), nullable=True)

    #Work and Experience
    has_work_experience = Column(Boolean, default=False, nullable=True)
    work_experience_lenght = Column(String, nullable=True)
    work_experience_description = Column(String, nullable=True)
    last_workplace = Column(String, nullable=True)
    last_position = Column(String, nullable=True)
    how_long_work = Column(String)
    why_work_with_us = Column(String)
    ever_recenptionist = Column(String)
    expected_salary = Column(String)

    #Documents
    photo_path = Column(String, nullable=True)
    resume_path = Column(String, nullable=True)

    #Additional info
    how_found_us = Column(String, nullable=True)
    additional_notes = Column(String, nullable=True)
    


    hr_notes = Column(Text, nullable=True)

    # Indexes
    __table_args__ = (
        Index("ix_applications_status_created", "status", "created_at"),
        Index("ix_applications_user_status", "user_id", "status"),
    )

    @validates("phone_number")
    def validate_phone(self, key, phone):
        # Basic phone validation for Uzbekistan
        cleaned = re.sub(r"[^\d+]", "", phone)
        if not re.match(r"^\+?998\d{9}$", cleaned):
            raise ValueError("Invalid Uzbekistan phone number")
        return cleaned