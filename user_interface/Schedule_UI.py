from typing import List, Optional
from datetime import date, time, datetime
from models.schedule import MasterSchedule, Appointment, AppointmentStatus
from models.masters import Master
from models.services import Service
from models.clients import Client

#Класс для вывода информации о расписании
class ScheduleUI:
    @staticmethod
    def show_master_schedule(master: Master, schedule_days: List[MasterSchedule]) -> None:
        """
        Показывает расписание мастера
        
        Args:
            master: Мастер
            schedule_days: Список дней расписания
        """
        print()
        print("РАСПИСАНИЕ МАСТЕРА:" + master.full_name)
        
        if not schedule_days:
            print("Расписание не найдено")
            print()
            return
        
        for day in schedule_days:
            if day.is_day_off:#type:ignore
                print(f"{day.work_date.strftime('%d.%m.%Y')}: Выходной")
            else:
                print(f"{day.work_date.strftime('%d.%m.%Y')}: {day.start_time.strftime('%H:%M')} - {day.end_time.strftime('%H:%M')}")
        print()
    
    @staticmethod
    def show_available_times(available_times: List[str]) -> None:
        """
        Показывает доступное время для записи
        
        Args:
            available_times: Список времени в формате ["09:00", "11:30", ...]
        """
        print()
        print("ДОСТУПНОЕ ВРЕМЯ:")
        
        if not available_times:
            print("Нет доступного времени")
            print()
            return
        
        for i, time_str in enumerate(available_times, 1):
            print(f"{i}) {time_str}")
        print()
    
    @staticmethod
    def show_available_masters(available_masters: List[Master]) -> None:
        """
        Показывает доступных мастеров
        
        Args:
            available_masters: Список мастеров
        """
        print()
        print("ДОСТУПНЫЕ МАСТЕРА:")
        
        if not available_masters:
            print("Нет доступных мастеров")
            print()
            return
        
        for i, master in enumerate(available_masters, 1):
            print(f"{i}) {master.full_name} - {master.specialty}")
        print()

class AppointmentUI:
    """Класс для отображения записей"""
    
    @staticmethod
    def show_appointment_details(appointment: Appointment) -> None:
        """
        Показывает детали записи
        
        Args:
            appointment: Запись
        """
        print("ИНФОРМАЦИЯ О ЗАПИСИ")
        print()
        print(f"ID: {appointment.appointment_id}")
        print(f"Дата и время: {appointment.start_datetime.strftime('%d.%m.%Y %H:%M')}")
        print(f"Мастер: {appointment.master.full_name}")
        print(f"Услуга: {appointment.service.service_name}")
        print(f"Длительность: {appointment.service.good_format_time}")
        print(f"Стоимость: {appointment.service.price} руб.")
        print(f"Статус: {appointment.status.value}")
        print()
    
    @staticmethod
    def show_client_appointments(appointments: List[Appointment]) -> None:
        """
        Показывает записи клиента
        
        Args:
            appointments: Список записей
        """
        if not appointments:
            print("У вас нет записей")
            print()
            return
        
        print("ВАШИ ЗАПИСИ:")
        print()
        
        for appointment in appointments:
            status_text = {
                AppointmentStatus.SCHEDULED.value: "[Запланирована]",
                AppointmentStatus.COMPLETED.value: "[Выполнена]",
                AppointmentStatus.CANCELLED.value: "[Отменена]",
                AppointmentStatus.NO_SHOW.value: "[Не явился]"
            }.get(appointment.status.value, "[Неизвестно]")
            
            print(f"{appointment.appointment_id}) {appointment.start_datetime.strftime('%d.%m.%Y %H:%M')} "
                  f"- {appointment.master.full_name} - {appointment.service.service_name} "
                  f"{status_text}")
        print()
    
    @staticmethod
    def show_appointment_created(appointment: Appointment) -> None:
        """
        Показывает сообщение об успешном создании записи
        
        Args:
            appointment: Созданная запись
        """
        print("ЗАПИСЬ СОЗДАНА УСПЕШНО!")
        print()
        print(f"Вы записаны на {appointment.start_datetime.strftime('%d.%m.%Y в %H:%M')}")
        print(f"Мастер: {appointment.master.full_name}")
        print(f"Услуга: {appointment.service.service_name}")
        print(f"Длительность: {appointment.service.good_format_time}")
        print(f"Стоимость: {appointment.service.price} руб.")
        print()
    
    @staticmethod
    def show_appointment_cancelled(appointment_id: int) -> None:
        """
        Показывает сообщение об отмене записи
        
        Args:
            appointment_id: ID отмененной записи
        """
        print(f"Запись {appointment_id} успешно отменена")
        print()
    
    @staticmethod
    def show_appointment_not_found(appointment_id: int) -> None:
        """
        Показывает что запись не найдена
        
        Args:
            appointment_id: ID записи
        """
        print(f"Запись с ID {appointment_id} не найдена")
        print()