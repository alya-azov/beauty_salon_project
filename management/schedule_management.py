from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, time, timedelta
from models.schedule import MasterSchedule, MasterBreak, Appointment, AppointmentStatus
from models.masters import Master
from models.services import Service
from models.clients import Client
from exceptions import ScheduleError

# для управления расписанием в бд
class ScheduleService:
    def __init__(self, session: Session):
        self.session = session
    
    def add_work_day(self, master_id: int, work_date: date, start_time: time, end_time: time) -> MasterSchedule:
        """
        Добавляет рабочий день для мастера
        
        Args:
            master_id: ID мастера
            work_date: Дата работы
            start_time: Время начала
            end_time: Время окончания
            is_day_off: Выходной день
            
        Returns:
            MasterSchedule: Созданное расписание
        """
        master = self.session.query(Master).filter_by(master_id=master_id).first()
        if not master:
            raise ScheduleError(f"Мастер с ID {master_id} не найден")
        
        existing = self.session.query(MasterSchedule).filter_by(master_id=master_id,work_date=work_date).first()
        
        if existing:
            raise ScheduleError(f"Расписание на {work_date} уже добавлено")
        
        schedule = MasterSchedule(master_id=master_id, work_date=work_date, start_time=start_time, end_time=end_time, is_day_off=False)
            
        self.session.add(schedule)
        self.session.commit()
        return schedule

    def add_break(self, schedule_id: int, break_start: time, break_end: time, reason: str = "") -> MasterBreak:
        """
        Добавляет перерыв в расписание мастера
        
        Args:
            schedule_id: ID расписания
            break_start: Начало перерыва
            break_end: Конец перерыва
            reason: Причина перерыва
            
        Returns:
            MasterBreak: Созданный перерыв
        """
        schedule = self.session.query(MasterSchedule).filter_by(schedule_id=schedule_id).first()
        if not schedule:
            raise ScheduleError(f"Расписание с ID {schedule_id} не найдено")
        
        if schedule.is_day_off: #type:ignore
            raise ScheduleError("Нельзя добавить перерыв в выходной день")
        
        if break_start < schedule.start_time or break_end > schedule.end_time: #type:ignore
            raise ScheduleError("Перерыв должен быть в пределах рабочего времени")
        
        master_break = MasterBreak(schedule_id=schedule_id, break_start=break_start, break_end=break_end, reason=reason)
        self.session.add(master_break)
        self.session.commit()
        return master_break

    def get_master_schedule(self, master_id: int, start_date: date, end_date: date) -> List[MasterSchedule]:
        """
        Получает расписание мастера на период
        
        Args:
            master_id: ID мастера
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            List[MasterSchedule]: Список расписаний
        """
        return self.session.query(MasterSchedule).filter(MasterSchedule.master_id == master_id, MasterSchedule.work_date >= start_date,
                                                         MasterSchedule.work_date <= end_date).order_by(MasterSchedule.work_date).all()
    
    def get_schedule_by_id(self, schedule_id: int) -> Optional[MasterSchedule]:
        """Получает расписание по его ID"""
        return self.session.query(MasterSchedule).filter_by(schedule_id=schedule_id).first()

    def get_schedule_by_date(self, master_id: int, work_date: date) -> Optional[MasterSchedule]:
        """Получает расписание мастера на конкретную дату"""
        return self.session.query(MasterSchedule).filter_by(master_id=master_id, work_date=work_date).first()
    
    def get_schedule_id_by_date(self, master_id: int, work_date: date) -> Optional[int]:
        """Получает id расписания мастера на конкретную дату"""
        schedule = self.get_schedule_by_date(master_id=master_id, work_date=work_date)
        if schedule:
            return schedule.schedule_id #type: ignore
        return None

    def get_available_time_slots(self, schedule_id: int, service_duration: int) -> List[datetime]:
        """
        Получает доступные временные слоты для записи
        
        Args:
            schedule_id: ID расписания
            service_duration: Длительность услуги в минутах
            
        Returns:
            List[datetime]: Список доступных времен начала
        """
        schedule = self.session.query(MasterSchedule).filter_by(schedule_id=schedule_id).first()
        if not schedule or schedule.is_day_off:#type:ignore
            return []
        
        breaks = schedule.breaks
        
        appointments = self.session.query(Appointment).filter(Appointment.schedule_id == schedule_id, Appointment.status == AppointmentStatus.SCHEDULED
                                                              ).order_by(Appointment.start_datetime).all()
        
        available_slots = []
        slot_duration = timedelta(minutes=service_duration)
        
        current_time = datetime.combine(schedule.work_date, schedule.start_time)#type:ignore
        end_time = datetime.combine(schedule.work_date, schedule.end_time)#type:ignore
        step = timedelta(minutes=30) 
        
        while current_time + slot_duration <= end_time:#type:ignore
            slot_end = current_time + slot_duration
            
            in_break = False
            for master_break in breaks:
                break_start = datetime.combine(schedule.work_date, master_break.break_start)#type:ignore
                break_end = datetime.combine(schedule.work_date, master_break.break_end)#type:ignore
                
                if current_time < break_end and slot_end > break_start:#type:ignore
                    in_break = True
                    current_time = break_end
                    break
            
            if not in_break:
                slot_available = True
                for appointment in appointments:
                    if current_time < appointment.end_datetime and slot_end > appointment.start_datetime:#type:ignore
                        slot_available = False
                        current_time = appointment.end_datetime
                        break
                
                if slot_available:
                    available_slots.append(current_time)
                    current_time += step
                else:
                    continue
            else:
                continue
        
        return available_slots

# для управления записями в бд
class AppointmentService:
    def __init__(self, session: Session):
        self.session = session
    
    def create_appointment(self, client_id: int, service_id: int, schedule_id: int, start_datetime: datetime, notes: str = "") -> Optional[Appointment]:
        """
        Создает новую запись
        
        Args:
            client_id: ID клиента
            service_id: ID услуги
            schedule_id: ID расписания (определяет мастера и дату)
            start_datetime: Дата и время начала
            notes: Дополнительные заметки
            
        Returns:
            Appointment: Созданная запись
        """

        client = self.session.query(Client).filter_by(client_id=client_id).first()
        if not client:
            raise ScheduleError(f"Клиент с ID {client_id} не найден")
        
        service = self.session.query(Service).filter_by(service_id=service_id).first()
        if not service:
            raise ScheduleError(f"Услуга с ID {service_id} не найдена")
        
        schedule = self.session.query(MasterSchedule).filter_by(schedule_id=schedule_id).first()
        if not schedule:
            raise ScheduleError(f"Расписание с ID {schedule_id} не найдено")
        
        
        master_id = schedule.master_id
        master = self.session.query(Master).filter_by(master_id=master_id).first()
        if not master:
            raise ScheduleError(f"Мастер с ID {master_id} не найден (в расписании {schedule_id})")
        if not any(cat.category_id == service.category_id for cat in master.service_categories):
            raise ScheduleError(f"Мастер {master.full_name} не может выполнять услугу '{service.service_name}'")

        
        if schedule.is_day_off:#type:ignore
            raise ScheduleError("Нельзя записаться на выходной день")
        
        end_datetime = start_datetime + timedelta(minutes=service.duration_minutes)#type:ignore
        
        work_start = datetime.combine(schedule.work_date, schedule.start_time)#type:ignore
        work_end = datetime.combine(schedule.work_date, schedule.end_time)#type:ignore
        
        if start_datetime < work_start or end_datetime > work_end:
            raise ScheduleError("Запись должна быть в пределах рабочего времени")
        
        for master_break in schedule.breaks:
            break_start = datetime.combine(schedule.work_date, master_break.break_start)#type:ignore
            break_end = datetime.combine(schedule.work_date, master_break.break_end)#type:ignore
            
            if (start_datetime < break_end and end_datetime > break_start):
                raise ScheduleError(f"Запись пересекается с перерывом ({master_break.break_start}-{master_break.break_end})")
        
        conflicting_appointments = self.session.query(Appointment).filter(Appointment.schedule_id == schedule_id, Appointment.start_datetime < end_datetime,
            Appointment.end_datetime > start_datetime, Appointment.status == AppointmentStatus.SCHEDULED).all()
        
        if conflicting_appointments:
            raise ScheduleError("Время уже занято другой записью")
        
        appointment = Appointment( master_id=master_id, client_id=client_id, service_id=service_id, schedule_id=schedule_id, start_datetime=start_datetime,
                                  end_datetime=end_datetime, status=AppointmentStatus.SCHEDULED, notes=notes)
            
        self.session.add(appointment)
        self.session.commit()
        return appointment

    def client_cancel_appointment(self, appointment_id: int, client_id: int) -> bool:
        """
        Клиент отменяет СВОЮ запись
        
        Args:
            appointment_id: ID записи
            client_id: ID клиента (должен совпадать с client_id в записи)
            
        Returns:
            bool: True если отмена успешна
        """
        appointment = self.session.query(Appointment).filter_by(appointment_id=appointment_id).first()
        if not appointment:
            raise ScheduleError(f"Запись с ID {appointment_id} не найдена")
        
        if appointment.client_id != client_id:#type:ignore
            raise ScheduleError("Вы можете отменять только свои записи")
        
        if appointment.status in [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW]:
            raise ScheduleError(f"Запись уже имеет статус {appointment.status.value}")
        
        appointment.status = AppointmentStatus.CANCELLED#type:ignore
        self.session.commit()
        return True
    
    def admin_cancel_appointment(self, appointment_id: int) -> bool:
        """
        Администратор отменяет ЛЮБУЮ запись
        
        Args:
            appointment_id: ID записи
            
        Returns:
            bool: True если отмена успешна
        """
        appointment = self.session.query(Appointment).filter_by(appointment_id=appointment_id).first()
        if not appointment:
            raise ScheduleError(f"Запись с ID {appointment_id} не найдена")
        
        if appointment.status in [AppointmentStatus.CANCELLED]:
            raise ScheduleError(f"Запись уже отменена")
        
        appointment.status = AppointmentStatus.CANCELLED#type:ignore
        self.session.commit()
        return True

    def get_client_appointments(self, client_id: int, status: Optional[AppointmentStatus]) -> List[Appointment]:
        """
        Получает записи клиента
        
        Args:
            client_id: ID клиента
            status: Фильтр по статусу
            
        Returns:
            List[Appointment]: Список записей клиента
        """
        client_appointments = self.session.query(Appointment).filter_by(client_id=client_id)
        
        if status:
            client_appointments = client_appointments.filter_by(status=status)
        
        return client_appointments.order_by(Appointment.start_datetime).all()
    
    def get_master_appointments(self, master_id: int, target_date: Optional[date]) -> List[Appointment]:
        """
        Получает записи мастера
        
        Args:
            master_id: ID мастера
            target_date: Фильтр по дате
            
        Returns:
            List[Appointment]: Список записей мастера
        """
        master_appointments = self.session.query(Appointment).filter_by(master_id=master_id)
        
        if target_date:
            master_appointments = master_appointments.filter(
                Appointment.start_datetime >= datetime.combine(target_date, time(0, 0)),
                Appointment.start_datetime < datetime.combine(target_date, time(23, 59, 59)))
        
        return master_appointments.order_by(Appointment.start_datetime).all()
    
    def find_available_masters(self, service_id: int, target_date: date) -> List[Master]:
        """
        Ищет мастеров, доступных для услуги на указанную дату
        
        Args:
            service_id: ID услуги
            target_date: Дата записи
            
        Returns:
            List[Master]: Список доступных мастеров
        """
        service = self.session.query(Service).filter_by(service_id=service_id).first()
        if not service:
            raise ScheduleError(f"Услуга с ID {service_id} не найдена")
        
        masters = self.session.query(Master).filter(Master.service_categories.any(category_id=service.category_id)).all()
        available_masters = []
        
        for master in masters:
            schedule = self.session.query(MasterSchedule).filter_by(master_id=master.master_id, work_date=target_date, is_day_off=False).first()
            
            if not schedule:
                continue
            
            schedule_service = ScheduleService(self.session)
            time_slots = schedule_service.get_available_time_slots(schedule_id=schedule.schedule_id, service_duration=service.duration_minutes)#type:ignore
            
            if not time_slots:
                continue       
        return available_masters