from models.schedule import MasterSchedule, MasterBreak, Appointment, AppointmentStatus
from models.masters import Master
from management.master_management import MasterService
from typing import List, Optional
from datetime import datetime, date

# Класс для вывода информации о расписании
class ScheduleUI:
    @staticmethod
    def show_schedule_details(schedule: Optional[MasterSchedule], appointments: Optional[List[Appointment]] = None) -> None:
        """
        Показывает детальную информацию о расписании мастера на день.
        
        Args:
            schedule: Объект расписания или None если не найден
            appointments: Список записей на этот день (опционально)
        """
        if not schedule:
            print("Расписание не найдено")
            return
        
        print("ИНФОРМАЦИЯ О РАСПИСАНИИ")
        print()
        print(f"ID расписания: {schedule.schedule_id}")
        print(f"ID мастера: {schedule.master_id}")
        print(f"Дата: {schedule.work_date}")
        print(f"Рабочие часы: {schedule.work_hours}")
        print(f"Выходной: {'Да' if schedule.is_day_off else 'Нет'}") #type: ignore
        print(f"Мастер: {schedule.master.full_name}")
        
        if schedule.breaks:
            print("Перерывы:") 
            i = 1
            for master_break in schedule.breaks:
                print(f"  {i}) {master_break.break_start.strftime('%H:%M')} - {master_break.break_end.strftime('%H:%M')}" + 
                      (f" ({master_break.reason})" if master_break.reason else ""))
                i += 1
        else:
            print("Перерывы: Нет")

        if appointments is not None:
            print("\nЗаписи на этот день:")
            i = 1
            for appointment in appointments:                    
                print(f" {i}) {appointment.start_datetime.strftime('%H:%M')} - Клиент: {appointment.client.full_name}")
                print(f"     Услуга: {appointment.service.service_name} | Статус: {appointment.status.value} | Длительность: {appointment.service.duration}")
                if appointment.notes: #type: ignore
                    print(f" Заметки: {appointment.notes}")
        else:
            print("\nНет записей на этот день")
        
        print()
    
    @staticmethod
    def show_schedule_list(schedules: List[MasterSchedule]) -> None:
        """
        Показывает список расписаний.
        
        Args:
            schedules: Список расписаний для отображения
        """
        if not schedules:
            print("Расписания не найдены")
            print()
            return
        
        print("СПИСОК РАСПИСАНИЙ")
        print()
        for schedule in schedules:
            print(f"  {schedule.schedule_id}) {schedule.work_date} - "
                  f"Мастер ID: {schedule.master_id} - {schedule.work_hours}")
        print()
    
    @staticmethod
    def show_schedule_created(schedule: MasterSchedule) -> None:
        """
        Сообщение об успешном создании расписания.
        
        Args:
            schedule: Созданное расписание
        """
        print(f"Расписание создано: {schedule.work_date} "
              f"({schedule.work_hours}")
        print(f"ID расписания: {schedule.schedule_id}")
        print()
    
    @staticmethod
    def show_break_created(master_break: MasterBreak) -> None:
        """
        Сообщение об успешном создании перерыва.
        
        Args:
            master_break: Созданный перерыв
        """
        print(f"Перерыв добавлен: {master_break.break_start.strftime('%H:%M')} - {master_break.break_end.strftime('%H:%M')}")
        if master_break.reason:#type: ignore
            print(f"Причина: {master_break.reason}")
        print()

    @staticmethod
    def show_available_time_slots(time_slots: List[datetime], master_id: int, master_service: MasterService, work_date: date) -> None:
        """
        Показывает доступные слоты с ID мастера, именем и датой.
    
        Args:
            time_slots: Список доступных временных слотов
            master_id: ID мастера
            master_service: Сервис для получения имени мастера
            work_date: Дата записи
        """
        master_name = master_service.get_master_name_by_id(master_id)
    
        if not time_slots:
            print(f"Нет доступных слотов у мастера {master_name} на {work_date}")
            print()
            return
    
        print(f"Доступные слоты у мастера {master_name} на {work_date}:")
        i = 1
        for slot in time_slots:
            print(f"  {i}) {slot.strftime('%H:%M')}")
            i += 1
        print()

# Класс для вывода информации о записях
class AppointmentUI:
    @staticmethod
    def show_appointment_details(appointment: Optional[Appointment]) -> None:
        """
        Показывает детальную информацию о записи.
        
        Args:
            appointment: Объект записи или None если не найден
        """
        if not appointment:
            print("Запись не найдена")
            return
        
        print("ИНФОРМАЦИЯ О ЗАПИСИ")
        print()
        print(f"ID записи: {appointment.appointment_id}")
        print(f"Статус: {appointment.status.value}")
        print(f"Дата и время: {appointment.start_datetime.strftime('%d.%m.%Y %H:%M')}")
        print(f"Длительность: {(appointment.end_datetime - appointment.start_datetime).seconds // 60} мин")
        print()
        
        if appointment.master:
            print(f"Мастер: {appointment.master.full_name}")
        else:
            print(f"Мастер ID: {appointment.master_id}")
        
        if appointment.client:
            print(f"Клиент: {appointment.client.full_name}")
        else:
            print(f"Клиент ID: {appointment.client_id}")
        
        if appointment.service:
            print(f"Услуга: {appointment.service.service_name}")
            print(f"Цена: {appointment.service.price} руб.")
        else:
            print(f"Услуга ID: {appointment.service_id}")
        
        if appointment.notes:#type: ignore
            print(f"Заметки: {appointment.notes}")
        
        print(f"Создана: {appointment.created_at.strftime('%d.%m.%Y %H:%M')}")
        print()
    
    @staticmethod
    def show_appointment_list(appointments: List[Appointment]) -> None:
        """
        Показывает список записей.
        
        Args:
            appointments: Список записей для отображения
        """
        if not appointments:
            print("Записи не найдены")
            print()
            return
        
        print("СПИСОК ЗАПИСЕЙ")
        print()
        for appointment in appointments:
            master_name = appointment.master.full_name
            client_name = appointment.client.full_name
            service_name = appointment.service.service_name
            
            print(f"{appointment.appointment_id}) {appointment.start_datetime.strftime('%d.%m.%Y %H:%M')}")
            print(f" Мастер: {master_name} | Клиент: {client_name}")
            print(f" Услуга: {service_name} | Статус: {appointment.status.value}")
            print()
    
    @staticmethod
    def show_appointment_created(appointment: Appointment) -> None:
        """
        Сообщение об успешном создании записи.
        
        Args:
            appointment: Созданная запись
        """
        print(f"Запись создана успешно!")
        print(f"ID записи: {appointment.appointment_id}")
        print(f"Дата и время: {appointment.start_datetime.strftime('%d.%m.%Y %H:%M')}")
        
        if appointment.master:
            print(f"Мастер: {appointment.master.full_name}")
        
        if appointment.service:
            print(f"Услуга: {appointment.service.service_name}")
        
        print()
    
    @staticmethod
    def show_appointment_cancelled(appointment_id: int, success: bool, by_client: bool = False) -> None:
        """
        Сообщение о результате отмены записи.
        
        Args:
            appointment_id: ID записи
            success: True если отменена, False если ошибка
            by_client: True если отмена клиентом, False если администратором
        """
        if success:
            who = "клиентом" if by_client else "администратором"
            print(f"Запись с ID {appointment_id} отменена {who}")
        else:
            print(f"Не удалось отменить запись с ID {appointment_id}")
        print()

    @staticmethod
    def show_available_masters(masters: List[Master], service_name: str, target_date: date) -> None:
        """
        Показывает доступных мастеров для услуги на дату.
        
        Args:
            masters: Список мастеров
            service_name: Название услуги
            target_date: Дата записи
        """
        if not masters:
            print(f"Нет доступных мастеров для услуги '{service_name}' на {target_date}")
            print()
            return
        
        print(f"ДОСТУПНЫЕ МАСТЕРА ДЛЯ УСЛУГИ '{service_name}' НА {target_date}")
        print()
        for i, master in enumerate(masters, 1):
            print(f"  {i}) {master.full_name} - {master.specialty}")
            print(f"     Телефон: {master.phone}")
            print()