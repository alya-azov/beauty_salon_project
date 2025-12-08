from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Time, Boolean, Enum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum
from models.base import Base

# класс для статусов записи
class AppointmentStatus(enum.Enum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"

#класс для работы с расписанием мастеров (на каждый день)
class MasterSchedule(Base):
    __tablename__ = "master_schedule"
    
    schedule_id = Column(Integer, primary_key=True)
    master_id = Column(Integer, ForeignKey('masters.master_id'), nullable=False)
    work_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_day_off = Column(Boolean, default=False, nullable=False)
    
    master = relationship("Master", back_populates="schedule")
    breaks = relationship("MasterBreak", back_populates="schedule_day", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="schedule_day")
    
    def __repr__(self) -> str:
        status = "Выходной" if self.is_day_off else f"{self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}" #type: ignore
        return f"MasterSchedule(master_id={self.master_id}, date={self.work_date}, {status})"
    
    @property
    def work_hours(self) -> str:
        """Возвращает рабочие часы в формате строки"""
        if self.is_day_off: #type: ignore
            return "Выходной"
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

#класс для работы с расписанием мастеров (перерывы)
class MasterBreak(Base):
    __tablename__ = "master_breaks"
    
    break_id = Column(Integer, primary_key=True)
    schedule_id = Column(Integer, ForeignKey('master_schedule.schedule_id'), nullable=False)
    break_start = Column(Time, nullable=False)
    break_end = Column(Time, nullable=False)
    reason = Column(String(100))  # Причина перерыва 
    
    schedule_day = relationship("MasterSchedule", back_populates="breaks")
    
    def __repr__(self) -> str:
        return f"MasterBreak({self.break_start.strftime('%H:%M')}-{self.break_end.strftime('%H:%M')})"

#класс для работы с записями
class Appointment(Base):
    __tablename__ = "appointments"
    
    appointment_id = Column(Integer, primary_key=True)
    master_id = Column(Integer, ForeignKey('masters.master_id'), nullable=False)
    client_id = Column(Integer, ForeignKey('clients.client_id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.service_id'), nullable=False)
    schedule_id = Column(Integer, ForeignKey('master_schedule.schedule_id'), nullable=False) 
    start_datetime = Column(DateTime, nullable=False) 
    end_datetime = Column(DateTime, nullable=False)
    status: Column[AppointmentStatus] = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    notes = Column(String(500))
    
    master = relationship("Master", back_populates="appointments")
    client = relationship("Client", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")
    schedule_day = relationship("MasterSchedule", back_populates="appointments")
    
    def __repr__(self) -> str:
        return f"Appointment({self.start_datetime.strftime('%d.%m.%Y %H:%M')}, {self.service.service_name})"