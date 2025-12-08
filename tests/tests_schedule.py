import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from management.schedule_management import ScheduleService
from models.schedule import MasterSchedule, Appointment, MasterBreak, AppointmentStatus
from models.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date, time

def test_master_schedule_class():
    """Тест класса MasterSchedule"""
    schedule = MasterSchedule(
        master_id=1,
        work_date=date(2025, 1, 15),
        start_time=time(9, 0),
        end_time=time(18, 0),
        is_day_off=False
    )
    
    assert schedule.master_id == 1#type:ignore
    assert schedule.work_date == date(2025, 1, 15)#type:ignore
    assert schedule.start_time == time(9, 0)#type:ignore
    assert schedule.end_time == time(18, 0)#type:ignore
    assert schedule.is_day_off == False#type:ignore
    assert schedule.work_hours == "09:00 - 18:00"
    
    print("test_master_schedule_class")

def test_master_schedule_day_off():
    """Тест выходного дня в расписании"""
    schedule = MasterSchedule(
        master_id=1,
        work_date=date(2025, 1, 1),
        start_time=time(0, 0),
        end_time=time(0, 0),
        is_day_off=True
    )
    
    assert schedule.is_day_off == True#type:ignore
    assert schedule.work_hours == "Выходной"
    
    print("test_master_schedule_day_off")

def test_master_break_class():
    """Тест класса MasterBreak"""
    master_break = MasterBreak(
        schedule_id=1,
        break_start=time(13, 0),
        break_end=time(14, 0),
        reason="Обед"
    )
    
    assert master_break.schedule_id == 1#type:ignore
    assert master_break.break_start == time(13, 0)#type:ignore
    assert master_break.break_end == time(14, 0)#type:ignore
    assert master_break.reason == "Обед"#type:ignore
    
    print("test_master_break_class")

def test_appointment_class():
    """Тест класса Appointment"""
    appointment = Appointment(
        master_id=1,
        client_id=1,
        service_id=1,
        schedule_id=1,
        start_datetime=datetime(2025, 1, 15, 10, 0),
        end_datetime=datetime(2025, 1, 15, 11, 0),
        status=AppointmentStatus.SCHEDULED,
        notes="Тестовая запись"
    )
    
    assert appointment.master_id == 1#type:ignore
    assert appointment.client_id == 1#type:ignore
    assert appointment.service_id == 1#type:ignore
    assert appointment.schedule_id == 1#type:ignore
    assert appointment.start_datetime == datetime(2025, 1, 15, 10, 0)#type:ignore
    assert appointment.end_datetime == datetime(2025, 1, 15, 11, 0)#type:ignore
    assert appointment.status == AppointmentStatus.SCHEDULED#type:ignore
    assert appointment.notes == "Тестовая запись"#type:ignore
    
    print("test_appointment_class")

def test_appointment_status_enum():
    """Тест enum статусов записи"""
    assert AppointmentStatus.SCHEDULED.value == "SCHEDULED"
    assert AppointmentStatus.COMPLETED.value == "COMPLETED"
    assert AppointmentStatus.CANCELLED.value == "CANCELLED"
    assert AppointmentStatus.NO_SHOW.value == "NO_SHOW"
    
    print("test_appointment_status_enum")

def test_schedule_service_add_work_day():
    """Тест добавления рабочего дня"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(engine)
    session = Session()

    from management.master_management import MasterService
    master_service = MasterService(session)
    master = master_service.create_master(
        first_name="Тест", last_name="Мастер", phone="+79991112233",
        email="test@test.ru", specialty="Парикмахер"
    )
    
    schedule_service = ScheduleService(session)
    schedule = schedule_service.add_work_day(
        master_id=master.master_id,#type:ignore
        work_date=date(2025, 1, 15),
        start_time=time(9, 0),
        end_time=time(18, 0)
    )
    
    assert schedule is not None
    assert schedule.master_id == master.master_id#type:ignore
    assert schedule.work_date == date(2025, 1, 15)#type:ignore
    assert schedule.start_time == time(9, 0)#type:ignore
    assert schedule.end_time == time(18, 0)#type:ignore
    assert schedule.is_day_off == False#type:ignore
    
    print("test_schedule_service_add_work_day")
    session.close()

def test_schedule_service_add_break():
    """Тест добавления перерыва"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(engine)
    session = Session()

    from management.master_management import MasterService
    master_service = MasterService(session)
    master = master_service.create_master(
        first_name="Тест", last_name="Мастер", phone="+79991112233",
        email="test@test.ru", specialty="Парикмахер"
    )
    
    schedule_service = ScheduleService(session)
    schedule = schedule_service.add_work_day(
        master_id=master.master_id,#type:ignore
        work_date=date(2025, 1, 15),
        start_time=time(9, 0),
        end_time=time(18, 0)
    )
    
    master_break = schedule_service.add_break(
        schedule_id=schedule.schedule_id,#type:ignore
        break_start=time(13, 0),
        break_end=time(14, 0),
        reason="Обед"
    )
    
    assert master_break is not None
    assert master_break.schedule_id == schedule.schedule_id#type:ignore
    assert master_break.break_start == time(13, 0)#type:ignore
    assert master_break.break_end == time(14, 0)#type:ignore
    assert master_break.reason == "Обед"#type:ignore
    
    print("test_schedule_service_add_break")
    session.close()

def run_all_tests():
    test_master_schedule_class()
    test_master_schedule_day_off()
    test_master_break_class()
    test_appointment_class()
    test_appointment_status_enum()
    test_schedule_service_add_work_day()
    test_schedule_service_add_break()
    
    print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")

if __name__ == "__main__":
    run_all_tests()