from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, date, timedelta
from models.base import Base

from auth.authentification import login_admin, simple_hash, login_client
from user_interface.Auth_UI import AuthUI, normalize_phone, format_phone

from models.clients import Client, SalonCard, DiscountLevel
from models.services import ServiceCategory, Service
from models.masters import Master
from models.schedule import AppointmentStatus, MasterSchedule, MasterBreak, Appointment

from management.client_management import ClientService, PurchaseService
from management.service_management import ServiceService, CategoryService
from management.master_management import MasterService, SpecialtyService
from management.schedule_management import ScheduleService, AppointmentService

from user_interface.Client_UI import ClientUI, PurchaseUI
from user_interface.Service_UI import ServiceUI, CategoryUI
from user_interface.Master_UI import MasterUI, SpecialtyUI
from user_interface.Schedule_UI import ScheduleUI, AppointmentUI

from typing import Optional
import sys
from exceptions import ClientError, ServiceError, MasterError, ScheduleError

engine = create_engine("postgresql://postgres:4321wwee@localhost:5432/salon_project")
Base.metadata.create_all(engine)
Session_ = sessionmaker(engine)
session = Session_()

class MainMenu:
    def __init__(self, session: Session):
        self.session = session
        self.current_client: Optional[Client] = None
        self.is_admin = False
        self.client_service = ClientService(session) 
    
    def show_main_auth_menu(self):
        """Главное меню аутентификации"""
        while True:
            print("\n" + "=" * 40)
            print("ВХОД В СИСТЕМУ ")
            print("=" * 40)
            print("1. Войти как клиент")
            print("2. Войти как администратор")
            print("3. Зарегистрироваться как новый клиент")
            print("0. Выход из программы")
            print("-" * 40)
            
            choice = input("Выберите действие: ").strip()
            
            if choice == "1":
                self.client_login()
                if self.current_client:
                    self.show_client_menu()
            elif choice == "2":
                self.admin_login()
                if self.is_admin:
                    self.show_admin_menu()
            elif choice == "3":
                self.client_registration()
            elif choice == "0":
                print("До свидания!")
                sys.exit(0)
            else:
                print("Неверный выбор. Попробуйте снова.")
###################################################################################################################################################
    def client_login(self):
        """Вход клиента"""
        self.current_client = login_client(self.session)
    
    def admin_login(self):
        """Вход администратора"""
        self.is_admin = login_admin()
    
    def client_registration(self):
        """Регистрация нового клиента"""
        try:    
            first_name, last_name, phone, email, password = AuthUI.show_client_registration_prompt()
            client = self.client_service.create_client(first_name=first_name,last_name=last_name, phone=normalize_phone(phone), email=email, password=password)
            AuthUI.show_registration_success(client)
        except ClientError as e:
            AuthUI.show_registration_error(str(e))
######################################################################################################################################################
    def show_settings_menu(self):
        """Меню настроек аккаунта клиента"""
        if not self.current_client:
            return
        
        while True:
            print("\n" + "=" * 40)
            print("НАСТРОЙКИ АККАУ1НТА")
            print("=" * 40)
            print(f"Клиент: {self.current_client.full_name}")
            print("=" * 40)
            print("1. Просмотреть мои данные")
            print("2. Изменить личные данные")
            print("3. Сменить пароль")
            print("4. Удалить аккаунт")
            print("0. Назад в меню клиента")
            print("-" * 40)
            
            choice = input("Выберите действие: ").strip()
            
            if choice == "1":
                self.view_my_data()
            elif choice == "2":
                self.edit_my_data()
            elif choice == "3":
                self.change_my_password()
            elif choice == "4":
                if self.delete_my_account():
                    return
            elif choice == "0":
                break
            else:
                print("Неверный выбор")
                print()

    def view_my_data(self):
        """Просмотр данных текущего клиента"""
        if not self.current_client:
            return
        ClientUI.show_client_details(self.current_client)
    
    def edit_my_data(self):
        """Изменение личных данных клиента"""
        client_service = ClientService(self.session)
        
        while True:
            print("\nКакие данные вы хотите изменить?")
            print("1. Имя")
            print("2. Фамилия")
            print("3. Телефон")
            print("4. Email")
            print("0. Назад")
            
            choice = input("Выберите действие: ").strip()
            
            try:
                if choice == "0":
                    break
                
                elif choice == "1":
                    new_first_name = input("Новое имя: ")
                    updated_client = client_service.update_client(self.current_client.client_id, "first_name", new_first_name) #type:ignore
                
                elif choice == "2":
                    new_last_name = input("Новая фамилия: ")
                    updated_client = client_service.update_client(self.current_client.client_id, "last_name", new_last_name)#type:ignore
                
                elif choice == "3":
                    new_phone = input("Новый телефон: ")
                    updated_client = client_service.update_client(self.current_client.client_id, "phone", new_phone)#type:ignore
                
                elif choice == "4":
                    new_email = input("Новый email: ")
                    updated_client = client_service.update_client(self.current_client.client_id, "email", new_email)#type:ignore
                else:
                    print("Неверный выбор.")
                ClientUI.show_client_updated(updated_client)
                self.current_client = updated_client
            
            except ClientError as e:
                print(f"Ошибка: {e}")
    
    def change_my_password(self):
        """Смена пароля текущим клиентом"""
        try:
            from user_interface.Auth_UI import AuthUI
            old_password, new_password, confirm_password = AuthUI.show_password_change_prompt()
            
            client_service = ClientService(self.session)
            success = client_service.change_password(self.current_client.client_id, old_password, new_password)#type:ignore
            
            ClientUI.show_password_changed(success, is_admin=False)
            
            if success:
                return True
        
        except ClientError as e:
            print(f"Ошибка: {e}")
    
    def delete_my_account(self):
        """Удаление аккаунта текущего клиента"""
        
        print("\nУДАЛЕНИЕ АККАУНТА")
        print(f"Будет удален аккаунт: {self.current_client.full_name}")#type:ignore
        
        confirm = input("Вы уверены? (да/нет): ").strip().lower()
        if confirm == "да" or confirm == "yes":
            try:
                client_service = ClientService(self.session)
                success = client_service.delete_client(self.current_client.client_id)#type:ignore
                    
                ClientUI.show_client_deleted(self.current_client.client_id, success)#type:ignore
                
                if success:
                    self.current_client = None
                    return True
            except ClientError as e:
                print(f"Ошибка: {e}")
        else:
            print("Удаление отменено.")        
        return False

###########################################################################################################################    
    def show_client_masters_menu(self):
        """Меню просмотра мастеров для клиента"""
        if not self.current_client:
            return
        
        master_service = MasterService(self.session)
        specialty_service = SpecialtyService(self.session)
        
        while True:
            print("\n" + "=" * 40)
            print("ПРОСМОТР МАСТЕРОВ")
            print("=" * 40)
            print("1. Показать всех мастеров")
            print("2. Найти мастера по специальности")
            print("3. Найти мастера по ID")
            print("0. Назад в меню клиента")
            print("-" * 40)
            
            choice = input("Выберите действие: ").strip()
            
            if choice == "1":
                masters = master_service.get_all_masters()
                if masters:
                    print("\n" + "=" * 40)
                    print("ВСЕ МАСТЕРА")
                    print("=" * 40)
                    MasterUI.show_masters_list(masters)
                    print("=" * 40)
                else:
                    print("Мастера не найдены")
            elif choice == "2":
                self.find_master_by_specialty(master_service, specialty_service)
            elif choice == "3":
                self.find_master_by_id(master_service)
            elif choice == "0":
                break
            else:
                print("Неверный выбор")
    
    def find_master_by_specialty(self, master_service, specialty_service):
        """Найти мастера по специальности"""
        specialties = specialty_service.get_all_specialties()
        if not specialties:
            print("Специальности не найдены")
            return
        
        print("\nДоступные специальности:")
        SpecialtyUI.show_all_specialties(specialties)
        
        try:
            choice = int(input("Выберите номер специальности: ").strip())
            if 1 <= choice <= len(specialties):
                selected_specialty = specialties[choice - 1]
                masters = specialty_service.get_masters_by_specialty(selected_specialty)
                
                if masters:
                    SpecialtyUI.show_masters_by_specialty(selected_specialty, masters)
                else:
                    print(f"Мастеров со специальностью '{selected_specialty}' не найдено")
            else:
                print("Неверный номер специальности")
        except ValueError:
            print("Введите число")
    
    def find_master_by_id(self, master_service):
        """Найти мастера по ID"""
        try:
            master_id = int(input("Введите ID мастера: ").strip())
            master = master_service.get_master_by_id(master_id)
            
            if master:
                MasterUI.show_master_details(master)
            else:
                print(f"Мастер с ID {master_id} не найден")
        except ValueError:
            print("ID должен быть числом")

#############################################################################################################################################

    def show_client_services_menu(self):
        """Меню просмотра услуг для клиента"""
        if not self.current_client:
            return
        
        service_service = ServiceService(self.session)
        category_service = CategoryService(self.session)
        
        while True:
            print("\n" + "=" * 40)
            print("НАШИ УСЛУГИ")
            print("=" * 40)
            print("1. Показать все услуги")
            print("2. Показать услуги по категории")
            print("3. Найти услугу по ID")
            print("4. Показать все категории")
            print("0. Назад в меню клиента")
            print("-" * 40)
            
            choice = input("Выберите действие: ").strip()
            
            if choice == "1":
                services = service_service.get_all_services()
                if services:
                    print("\n" + "=" * 40)
                    print("ВСЕ УСЛУГИ")
                    print("=" * 40)
                    ServiceUI.show_services_list(services)
                    print("=" * 40)
                else:
                    print("Услуги не найдены")
            elif choice == "2":
                self.view_services_by_category(service_service, category_service)
            elif choice == "3":
                self.find_service_by_id(service_service)
            elif choice == "4":
                self.view_all_categories(category_service)
            elif choice == "0":
                break
            else:
                print("Неверный выбор")
    
    def view_services_by_category(self, service_service, category_service):
        """Показать услуги по категории"""
        categories = category_service.get_all_categories()
        if not categories:
            print("Категории не найдены")
            return
        
        print("\nДоступные категории:")
        CategoryUI.show_all_categories(categories)
        
        try:
            choice = int(input("\nВыберите номер категории: ").strip())
            if 1 <= choice <= len(categories):
                selected_category = categories[choice - 1]
                services = service_service.get_services_by_category(selected_category.category_id)
                
                if services:
                    print(f"\nУслуги категории '{selected_category.category_name}':")
                    print()
                    ServiceUI.show_services_by_category(selected_category, services)
                    print("=" * 40)
                else:
                    print(f"В категории '{selected_category.category_name}' нет услуг")
            else:
                print("Неверный номер категории")
        except ValueError:
            print("Введите число")
    
    def find_service_by_id(self, service_service):
        """Найти услугу по ID"""
        try:
            service_id = int(input("Введите ID услуги: ").strip())
            service = service_service.get_service_by_id(service_id)
            
            if service:
                ServiceUI.show_service_details(service)
            else:
                print(f"Услуга с ID {service_id} не найдена")
        except ValueError:
            print("ID должен быть числом")
    
    def view_all_categories(self, category_service):
        """Показать все категории"""
        categories = category_service.get_all_categories()
        if categories:
            print("\n" + "=" * 40)
            print("ВСЕ КАТЕГОРИИ УСЛУГ")
            print("=" * 40)
            CategoryUI.show_all_categories(categories)
            print("=" * 40)
        else:
            print("Категории не найдены")

#############################################################################################################################################

    def show_client_appointment_menu(self):
        """Меню управления записями для клиента"""
        if not self.current_client:
            print("Нужно войти в систему")
            return
        
        while True:
            print("\n" + "=" * 40)
            print("УПРАВЛЕНИЕ ЗАПИСЯМИ")
            print("=" * 40)
            print("1. Записаться на новую услугу")
            print("2. Посмотреть все мои записи")
            print("3. Посмотреть предстоящие записи")
            print("4. Посмотреть выполненные записи")
            print("5. Отменить запись")
            print("0. Назад в меню клиента")
            print("=" * 40)
            
            choice = input("Выберите действие: ").strip()
            
            if choice == "1":
                self.make_an_appointment_client()
            elif choice == "2":
                self.show_all_client_appointments()
            elif choice == "3":
                self.show_upcoming_client_appointments()
            elif choice == "4":
                self.show_completed_client_appointments()
            elif choice == "5":
                self.cancel_client_appointment()
            elif choice == "0":
                break
            else:
                print("Неверный выбор")
    
    def make_an_appointment_client(self):
        """Создание записи на услугу для клиента"""
        if not self.current_client:
            print("Нужно войти в систему")
            return
        
        appointment_service = AppointmentService(self.session)
        service_service = ServiceService(self.session)
        master_service = MasterService(self.session)
        schedule_service = ScheduleService(self.session)
        
        print("\n" + "=" * 40)
        print("ЗАПИСЬ НА УСЛУГУ")
        print("=" * 40)
        
        try:
            # 1. service
            services = service_service.get_all_services()
            if not services:
                print("Нет доступных услуг")
                return
            print("\nДоступные услуги:")
            ServiceUI.show_services_list(services)
            service_id = int(input("\nID услуги: ").strip())
            service = service_service.get_service_by_id(service_id)
            if not service:
                print(f"Услуга с ID {service_id} не найдена")
                return
            print(f"Услуга: {service.service_name} ({service.good_format_time}, {service.price} руб.)")
            
            # 2. date
            date_str = input("Дата записи (ДД.ММ.ГГГГ): ").strip()
            work_date = datetime.strptime(date_str, "%d.%m.%Y").date()
            if work_date < date.today():
                print("Нельзя создавать записи на прошедшие даты")
                return
            
            # 3. masters 
            all_masters = master_service.get_all_masters()
            suitable_masters = []
            
            for master in all_masters:
                if not any(cat.category_id == service.category_id for cat in master.service_categories):
                    continue
                
                schedule = schedule_service.get_schedule_by_date(master.master_id, work_date)#type: ignore
                if not schedule:
                    continue

                time_slots = schedule_service.get_available_time_slots(schedule_id=schedule.schedule_id, service_duration=service.duration_minutes)#type: ignore
                if not time_slots:
                    continue
                
                suitable_masters.append(master)
            
            if not suitable_masters:
                print(f"Нет доступных мастеров для услуги '{service.service_name}' на {date_str}")
                print("Причины: мастера не умеют эту услугу, нет расписания или нет свободных слотов")
                return
            
            print(f"\nМастера, доступные для '{service.service_name}' на {date_str}:")
            i = 1
            for master in suitable_masters:
                print(f"{i}. {master.full_name} - {master.specialty}")
                i += 1
            
            # 4. master choice
            master_choice = int(input("\nВыберите номер мастера: ").strip())
            if not (1 <= master_choice <= len(suitable_masters)):
                print("Неверный номер мастера")
                return
            
            selected_master = suitable_masters[master_choice - 1]
            master_id = selected_master.master_id
            
            schedule = schedule_service.get_schedule_by_date(master_id, work_date)
            time_slots = schedule_service.get_available_time_slots(schedule_id=schedule.schedule_id, service_duration=service.duration_minutes)#type: ignore

            print(f"\nДоступные слоты у мастера {selected_master.full_name} на {date_str}:")
            i = 1
            for slot in time_slots:
                print(f"{i}) {slot.strftime('%H:%M')}")
                i += 1
            
            # 5. time choice
            time_choice = int(input("\nВыберите номер слота: ").strip())
            if not (1 <= time_choice <= len(time_slots)):
                print("Неверный номер слота")
                return
            
            start_datetime = time_slots[time_choice - 1]
            
            # 6. notes
            notes = input("Заметки (необязательно): ").strip()

            # 7. making an appointment
            appointment = appointment_service.create_appointment(
                client_id=self.current_client.client_id, #type: ignore
                service_id=service_id, 
                schedule_id=schedule.schedule_id, #type: ignore
                start_datetime=start_datetime, 
                notes=notes
            )
            
            if appointment:
                AppointmentUI.show_appointment_created(appointment)
            else:
                print("Не удалось создать запись")
            
        except ValueError as e:
            print(f"Ошибка ввода: {e}")
        except ScheduleError as e:
            print(f"Ошибка: {e}")
    
    def show_all_client_appointments(self):
        """Показать все записи клиента"""

        appointment_service = AppointmentService(self.session)
        appointments = appointment_service.get_client_appointments(self.current_client.client_id)#type: ignore
        
        if not appointments:
            print("\nУ вас пока нет записей")
            return
        
        print("\n" + "=" * 40)
        print("ВСЕ МОИ ЗАПИСИ")
        print("=" * 40)
        AppointmentUI.show_appointment_list(appointments)
    
    def show_upcoming_client_appointments(self):
        """Показать предстоящие записи клиента"""
        
        appointment_service = AppointmentService(self.session)
        from models.schedule import AppointmentStatus
        appointments = appointment_service.get_client_appointments(self.current_client.client_id, status=AppointmentStatus.SCHEDULED)#type: ignore
        
        if not appointments:
            print("\nУ вас нет предстоящих записей")
            return
        
        print("\n" + "=" * 40)
        print("ПРЕДСТОЯЩИЕ ЗАПИСИ")
        print("=" * 40)
        AppointmentUI.show_appointment_list(appointments)
    
    def show_completed_client_appointments(self):
        """Показать выполненные записи клиента"""
        
        appointment_service = AppointmentService(self.session)
        from models.schedule import AppointmentStatus
        appointments = appointment_service.get_client_appointments(self.current_client.client_id, status=AppointmentStatus.COMPLETED)#type: ignore
        
        if not appointments:
            print("\nУ вас нет выполненных записей")
            return
        
        print("\n" + "=" * 40)
        print("ВЫПОЛНЕННЫЕ ЗАПИСИ")
        print("=" * 40)
        AppointmentUI.show_appointment_list(appointments)
    
    def cancel_client_appointment(self):
        """Отмена записи клиентом"""
        appointment_service = AppointmentService(self.session)
        
        print("\n" + "=" * 40)
        print("ОТМЕНА ЗАПИСИ")
        print("=" * 40)
        
        from models.schedule import AppointmentStatus
        appointments = appointment_service.get_client_appointments(self.current_client.client_id,  status=AppointmentStatus.SCHEDULED)#type: ignore
        
        if not appointments:
            print("У вас нет предстоящих записей для отмены")
            return
        
        print("\nВаши предстоящие записи:")
        i = 1
        for appointment in appointments:
            print(f"{i}) #{appointment.appointment_id} - {appointment.start_datetime.strftime('%d.%m.%Y %H:%M')}")
            print(f"   Услуга: {appointment.service.service_name}")
            print(f"   Мастер: {appointment.master.full_name}")
            i += 1
        
        try:
            choice = int(input("\nВыберите номер записи для отмены (0 - отмена): ").strip())
            
            if choice == 0:
                print("Отмена операции")
                return
            
            if not (1 <= choice <= len(appointments)):
                print("Неверный номер записи")
                return
            
            selected_appointment = appointments[choice - 1]
            success = appointment_service.client_cancel_appointment(selected_appointment.appointment_id, self.current_client.client_id)#type: ignore
                    
            if success:
                print("Запись успешно отменена!")
            else:
                print("Не удалось отменить запись")
                
        except ValueError:
            print("Введите число")
        except Exception as e:
            print(f"Произошла ошибка: {e}")

#############################################################################################################################################

    def show_client_menu(self):
        """Меню для клиента"""
        
        print("\n" + "=" * 40)
        print("МЕНЮ КЛИЕНТА")
        print("=" * 40)
        print(f"Добро пожаловать, {self.current_client.full_name}!")#type:ignore

        while True:
            print("\n МЕНЮ КЛИЕНТА")
            print("1. Настройки аккаунта")
            print("2. Просмотр мастеров")
            print("3. Просмотр услуг")
            print("4. Записаться на услугу салона красоты")
            print("0. Выйти")
        
            choice = input("Выберите действие: ")

            if choice == "1":
                self.show_settings_menu()
                if self.current_client is None:
                    return
            elif choice == "2":
                self.show_client_masters_menu()
            elif choice == "3":
                self.show_client_services_menu()
            elif choice == "4":
                self.show_client_appointment_menu()
            elif choice == "0":
                break
            else:
                print("Неверный выбор")
        self.current_client = None

##########################################################################################

    def manage_services(self):
        """Управление услугами (админ)"""
        service_service = ServiceService(self.session)
        category_service = CategoryService(self.session)
        
        while True:
            print("\n" + "=" * 40)
            print("УПРАВЛЕНИЕ УСЛУГАМИ")
            print("=" * 40)
            print("1. Показать все услуги")
            print("2. Добавить услугу")
            print("3. Удалить услугу")
            print("4. Найти услугу по ID")
            print("5. Показать услуги по категории")
            print("6. Показать все категории")
            print("7. Добавить новую категорию")
            print("8. Обновить услугу")
            print("9. Удалить категорию")
            print("0. Назад в меню администратора")
            print("-" * 40)
            
            choice = input("Выберите действие: ").strip()
            
            if choice == "1":
                services = service_service.get_all_services()
                if services:
                    ServiceUI.show_services_list(services)
                else:
                    print("Услуги не найдены")
            
            elif choice == "2":
                self.add_new_service(service_service, category_service)
            
            elif choice == "3":
                try:
                    service_id = int(input("Введите ID услуги для удаления: ").strip())
                    confirm = input(f"Вы уверены что хотите удалить услугу с ID {service_id}? (да/нет): ").lower()
                    if confirm == "да":
                        success = service_service.delete_service(service_id)
                        ServiceUI.show_service_deleted(service_id, success)
                except ValueError:
                    print("ID должен быть числом")
                except ServiceError as e:
                    print(f"Ошибка: {e}")
            
            elif choice == "4":
                try:
                    service_id = int(input("Введите ID услуги: ").strip())
                    service = service_service.get_service_by_id(service_id)
                    if service:
                        ServiceUI.show_service_details(service)
                    else:
                        print(f"Услуга с ID {service_id} не найдена")
                except ValueError:
                    print("ID должен быть числом")
            
            elif choice == "5":
                self.show_services_by_category_admin(service_service, category_service)
            
            elif choice == "6":
                categories = category_service.get_all_categories()
                if categories:
                    CategoryUI.show_all_categories(categories)
                else:
                    print("Категории не найдены")
            
            elif choice == "7":
                category_name = input("Введите название новой категории: ").strip()
                try:
                    category = category_service.create_category(category_name)
                    CategoryUI.show_category_created(category)
                except ServiceError as e:
                    print(f"Ошибка: {e}")
            
            elif choice == "8":
                self.update_service_admin(service_service, category_service)
            
            elif choice == "9":
                try:
                    category_id = int(input("Введите ID категории для удаления: ").strip())
                    success = category_service.delete_category(category_id)
                    CategoryUI.show_category_deleted(category_id, success)
                except ValueError:
                    print("ID должен быть числом")
                except ServiceError as e:
                    print(f"Ошибка: {e}")
            
            elif choice == "0":
                break
            
            else:
                print("Неверный выбор.")
    
    def add_new_service(self, service_service, category_service):
        """Добавление новой услуги"""
        print("\n" + "=" * 40)
        print("ДОБАВЛЕНИЕ НОВОЙ УСЛУГИ")
        print("=" * 40)
        

        categories = category_service.get_all_categories()
        
        print("Доступные категории:")
        i = 1
        for category in categories:
            print(f"{i}. {category.category_name} (ID: {category.category_id})")
            i += 1
        
        try:
            service_name = input("\nНазвание услуги: ").strip()
            if not service_name:
                print("Название не может быть пустым!")
                return
            
            duration_str = input("Длительность в минутах (кратно 30): ").strip()
            price_str = input("Цена (руб.): ").strip()
            category_choice = int(input("Выберите номер категории: ").strip())
            
            if not (1 <= category_choice <= len(categories)):
                print("Неверный номер категории!")
                return
            
            selected_category = categories[category_choice - 1]
            
            service = service_service.create_service(
                service_name=service_name,
                duration_minutes=int(duration_str),
                price=int(price_str),
                category_id=selected_category.category_id
            )
            
            ServiceUI.show_service_created(service)
            
        except ValueError:
            print("Убедитесь что длительность и цена - числа")
        except ServiceError as e:
            print(f"Ошибка: {e}")
    
    def show_services_by_category_admin(self, service_service, category_service):
        """Показать услуги по категории"""
        categories = category_service.get_all_categories()
        if not categories:
            print("Категории не найдены")
            return
        
        print("\nДоступные категории:")
        i = 1
        for category in categories:
            print(f"{i}. {category.category_name} (ID: {category.category_id})")
            i += 1
        
        try:
            choice = int(input("\nВыберите номер категории: ").strip())
            if 1 <= choice <= len(categories):
                selected_category = categories[choice - 1]
                services = service_service.get_services_by_category(selected_category.category_id)
                
                if services:
                    print(f"\nУслуги категории '{selected_category.category_name}':")
                    ServiceUI.show_services_list(services)
                else:
                    print(f"В категории '{selected_category.category_name}' нет услуг")
            else:
                print("Неверный номер категории")
        except ValueError:
            print("Введите число")
        
    def update_service_admin(self, service_service, category_service):
        """Обновление услуги"""
        try:
            service_id = int(input("Введите ID услуги для обновления: ").strip())
            service = service_service.get_service_by_id(service_id)
            
            if not service:
                print(f"Услуга с ID {service_id} не найдена")
                return
            
            ServiceUI.show_service_details(service)
            
            print("\nКакое поле вы хотите обновить?")
            print("1. Название услуги")
            print("2. Длительность")
            print("3. Цена")
            print("4. Категория")
            
            field_choice = input("Выберите поле: ").strip()
            
            if field_choice == "1":
                new_name = input("Новое название: ").strip()
                updated_service = service_service.update_service(service_id, "service_name", new_name)
                ServiceUI.show_service_updated(updated_service)
            
            elif field_choice == "2":
                new_duration = input("Новая длительность (минут, кратно 30): ").strip()
                updated_service = service_service.update_service(service_id, "duration_minutes", new_duration)
                ServiceUI.show_service_updated(updated_service)
            
            elif field_choice == "3":
                new_price = input("Новая цена (руб.): ").strip()
                updated_service = service_service.update_service(service_id, "price", new_price)
                ServiceUI.show_service_updated(updated_service)
            
            elif field_choice == "4":
                categories = category_service.get_all_categories()
                if not categories:
                    print("Категории не найдены")
                    return
                
                print("Доступные категории:")
                i = 1
                for category in categories:
                    print(f"{i}. {category.category_name} (ID: {category.category_id})")
                    i += 1
                
                cat_choice = int(input("Выберите номер новой категории: ").strip())
                if 1 <= cat_choice <= len(categories):
                    selected_category = categories[cat_choice - 1]
                    updated_service = service_service.update_service(service_id, "category_id", str(selected_category.category_id))
                    ServiceUI.show_service_updated(updated_service)
                else:
                    print("Неверный номер категории")
            
            else:
                print("Неверный выбор поля")
        
        except ValueError:
            print("Ошибка ввода: ID должен быть числом")
        except ServiceError as e:
            print(f"Ошибка: {e}")

#####################################################################################################################

    def manage_clients(self):
        """Управление клиентами (админ)"""
        client_service = ClientService(self.session)
        purchase_service = PurchaseService(self.session)
        
        while True:
            print("\n" + "=" * 40)
            print("УПРАВЛЕНИЕ КЛИЕНТАМИ")
            print("=" * 40)
            print("1. Поиск клиента по ID")
            print("2. Поиск клиента по телефону")
            print("3. Редактирование данных клиента")
            print("4. Изменение пароля клиента")
            print("5. Добавление покупки клиенту")
            print("6. Просмотр записей клиента")
            print("7. Удаление клиента")
            print("0. Возврат в меню администратора")
            print("-" * 40)
            
            choice = input("Выберите действие: ").strip()
            
            if choice == "1":
                self.find_client_by_id(client_service)
            
            elif choice == "2":
                self.find_client_by_phone(client_service)
            
            elif choice == "3":
                self.edit_client_data(client_service)
            
            elif choice == "4":
                self.change_client_password_admin(client_service)
            
            elif choice == "5":
                self.add_client_purchase(client_service, purchase_service)
            
            elif choice == "6":
                self.show_client_appointments_admin()
                print("Функция в разработке...")

            elif choice == "7":
                self.delete_client_admin(client_service)
            
            elif choice == "0":
                break
            
            else:
                print("Неверный выбор.")
    
    def find_client_by_id(self, client_service):
        """Поиск клиента по ID"""
        try:
            client_id = int(input("Введите ID клиента: ").strip())
            client = client_service.get_client_by_id(client_id)
            
            if client:
                ClientUI.show_client_details(client)
            else:
                print(f"Клиент с ID {client_id} не найден")
        except ValueError:
            print("ID должен быть числом")
    
    def find_client_by_phone(self, client_service):
        """Поиск клиента по телефону"""
        phone = input("Введите телефон клиента: ").strip()
        client = client_service.get_client_by_phone(phone)
        
        if client:
            ClientUI.show_client_details(client)
        else:
            print(f"Клиент с телефоном {phone} не найден")
    
    def edit_client_data(self, client_service):
        """Редактирование данных клиента"""
        try:
            client_id = int(input("Введите ID клиента для редактирования: ").strip())
            client = client_service.get_client_by_id(client_id)
            
            if not client:
                print(f"Клиент с ID {client_id} не найден")
                return
            
            print("\nКакие данные вы хотите изменить?")
            print("1. Имя")
            print("2. Фамилия")
            print("3. Телефон")
            print("4. Email")
            print("0. Отмена")
            
            choice = input("Выберите поле: ").strip()
            
            try:
                if choice == "1":
                    new_first_name = input("Новое имя: ").strip()
                    updated_client = client_service.update_client(client_id, "first_name", new_first_name)
                
                elif choice == "2":
                    new_last_name = input("Новая фамилия: ").strip()
                    updated_client = client_service.update_client(client_id, "last_name", new_last_name)
                
                elif choice == "3":
                    new_phone = input("Новый телефон: ").strip()
                    updated_client = client_service.update_client(client_id, "phone", new_phone)
                
                elif choice == "4":
                    new_email = input("Новый email: ").strip()
                    updated_client = client_service.update_client(client_id, "email", new_email)
                
                elif choice == "0":
                    print("Редактирование отменено")
                
                else:
                    print("Неверный выбор")
                
                ClientUI.show_client_updated(updated_client)
            
            except ClientError as e:
                print(f"Ошибка: {e}")
        
        except ValueError:
            print("ID должен быть числом")
    
    def change_client_password_admin(self, client_service):
        """Изменение пароля клиента администратором"""
        try:
            client_id = int(input("Введите ID клиента: ").strip())
            client = client_service.get_client_by_id(client_id)
            
            if not client:
                print(f"Клиент с ID {client_id} не найден")
                return
            
            new_password = input("Новый пароль: ").strip()
            confirm_password = input("Подтвердите пароль: ").strip()
            
            if new_password != confirm_password:
                print("Пароли не совпадают!")
                return
            
            success = client_service.admin_change_password(client_id, new_password)
            ClientUI.show_password_changed(success, is_admin=True)
        
        except ValueError:
            print("ID должен быть числом")
        except ClientError as e:
            print(f"Ошибка: {e}")

    
    def add_client_purchase(self, client_service, purchase_service):
        """Добавление покупки клиенту"""
        try:
            client_id = int(input("Введите ID клиента: ").strip())
            client = client_service.get_client_by_id(client_id)
            
            if not client:
                print(f"Клиент с ID {client_id} не найден")
                return
            
            ClientUI.show_client_details(client)
            
            try:
                amount = float(input("Сумма покупки (руб.): ").strip())
                client, discounted_amount, old_level, new_level = purchase_service.add_purchase(client_id, amount)
                PurchaseUI.show_purchase_result(client, discounted_amount, old_level, new_level)
            
            except ValueError:
                print("Сумма должна быть числом")
            except ClientError as e:
                PurchaseUI.show_purchase_error(str(e))
        
        except ValueError:
            print("ID должен быть числом")
        
    
    def delete_client_admin(self, client_service):
        """Удаление клиента администратором"""
        try:
            client_id = int(input("Введите ID клиента для удаления: ").strip())
            client = client_service.get_client_by_id(client_id)
            
            if not client:
                print(f"Клиент с ID {client_id} не найден")
                return
            
            ClientUI.show_client_details(client)
            
            confirm = input("\nВы уверены что хотите удалить этого клиента? (да/нет): ").strip().lower()
            
            if confirm == "да":
                success = client_service.delete_client(client_id)
                ClientUI.show_client_deleted(client_id, success)
            else:
                print("Удаление отменено")
        
        except ValueError:
            print("ID должен быть числом")
        except ClientError as e:
            print(f"Ошибка: {e}")
    
    def show_client_appointments_admin(self):
        """Просмотр записей клиента (администратором)"""
        client_service = ClientService(self.session)
        appointment_service = AppointmentService(self.session)
        
        print("\n" + "=" * 40)
        print("ПРОСМОТР ЗАПИСЕЙ КЛИЕНТА")
        print("=" * 40)
        
        # 1. client
        phone = input("Введите телефон клиента: ").strip()
        client = client_service.get_client_by_phone(phone)
        if not client:
            print(f"Клиент с телефоном {phone} не найден")
            return
        
        print(f"\nКлиент: {client.full_name} (ID: {client.client_id})")
        
        # 2. appointments
        print("\nКакие записи показать?")
        print("1. Все записи")
        print("2. Только предстоящие")
        print("3. Только выполненные")
        
        try:
            filter_choice = input("Выберите фильтр (1-3): ").strip()
            
            status_filter = None
            from models.schedule import AppointmentStatus
            
            if filter_choice == "2":
                status_filter = AppointmentStatus.SCHEDULED
            elif filter_choice == "3":
                status_filter = AppointmentStatus.COMPLETED
            elif filter_choice != "1":
                print("Неверный выбор")
                return
            appointments = appointment_service.get_client_appointments(client.client_id, status=status_filter)#type:ignore
            if not appointments:
                print("\nУ клиента нет записей" + 
                      (f" со статусом {status_filter.value}" if status_filter else ""))
                return
            
            print(f"\nЗАПИСИ КЛИЕНТА {client.full_name}:")
            print("=" * 40)
            
            AppointmentUI.show_appointment_list(appointments)
                
        except ValueError:
            print("Ошибка ввода")
        except Exception as e:
            print(f"Произошла ошибка: {e}")
    
    def show_appointment_details_admin(self, appointment_service):
        """Показать детали конкретной записи"""
        try:
            appointment_id = int(input("\nВведите ID записи: ").strip())
            from models.schedule import Appointment
            appointment = self.session.query(Appointment).filter_by(appointment_id=appointment_id).first()
            
            if appointment:
                from user_interface.Schedule_UI import AppointmentUI
                AppointmentUI.show_appointment_details(appointment)
            else:
                print(f"Запись с ID {appointment_id} не найдена")
        
        except ValueError:
            print("ID должен быть числом")
    
    def cancel_appointment_for_client_admin(self, appointment_service):
        """Отмена записи для клиента администратором"""
        try:
            appointment_id = int(input("\nВведите ID записи для отмены: ").strip())
            
            from models.schedule import Appointment
            appointment = self.session.query(Appointment).filter_by(appointment_id=appointment_id).first()
            if not appointment:
                print(f"Запись с ID {appointment_id} не найдена")
                return
            
            from user_interface.Schedule_UI import AppointmentUI
            AppointmentUI.show_appointment_details(appointment)
            
            confirm = input("\nВы уверены, что хотите отменить эту запись? (да/нет): ").strip().lower()
            if confirm == "да":
                success = appointment_service.admin_cancel_appointment(appointment_id)
                
                if success:
                    print("Запись успешно отменена администратором")
                else:
                    print("Не удалось отменить запись")
            else:
                print("Отмена отменена")
        
        except ValueError:
            print("ID должен быть числом")
        except ScheduleError as e:
            print(f"Ошибка: {e}")
    
    def change_appointment_status_for_client(self, appointment_service):
        """Изменение статуса записи для клиента"""
        try:
            appointment_id = int(input("\nВведите ID записи: ").strip())
            
            from models.schedule import Appointment, AppointmentStatus
            appointment = self.session.query(Appointment).filter_by(appointment_id=appointment_id).first()
            if not appointment:
                print(f"Запись с ID {appointment_id} не найдена")
                return
            
            from user_interface.Schedule_UI import AppointmentUI
            AppointmentUI.show_appointment_details(appointment)
            
            print("\nВСЕ СТАТУСЫ ЗАПИСИ:")
            print("1. SCHEDULED - Запланировано")
            print("2. COMPLETED - Выполнено")
            print("3. CANCELLED - Отменено")
            print("4. NO_SHOW - Неявка")
            
            status_map = {"1": AppointmentStatus.SCHEDULED, "2": AppointmentStatus.COMPLETED,
                          "3": AppointmentStatus.CANCELLED, "4": AppointmentStatus.NO_SHOW}
            
            choice = input("\nВыберите новый статус (1-4): ").strip()
            
            if choice not in status_map:
                print("Неверный выбор")
                return
            
            selected_status = status_map[choice]
            current_status = appointment.status
            
            try:
                success = appointment_service.update_appointment_status(appointment_id, selected_status)
                
                if success:
                    print(f"Статус изменен с {current_status.value} на {selected_status.value}")
                    
                    # Если статус изменен на ВЫПОЛНЕНО, добавляем покупку
                    if selected_status == AppointmentStatus.COMPLETED:
                        confirm = input("Вы уверены, что хотите изменить статус на ВЫПОЛНЕНО? (да/нет): ").lower().strip()
                        if confirm == "да":
                            try:
                                purchase_service = PurchaseService(self.session)
                                
                                amount = float(appointment.service.price)
                                client, discounted_amount, old_level, new_level = purchase_service.add_purchase(
                                    appointment.client_id, amount #type: ignore
                                )
                                
                                from user_interface.Client_UI import PurchaseUI
                                PurchaseUI.show_purchase_result(client, discounted_amount, old_level, new_level)
                                
                            except Exception as e:
                                print(f"Не удалось добавить покупку: {e}")
                else:
                    print("Не удалось изменить статус")
            
            except Exception as e:
                print(f"Ошибка при изменении статуса: {e}")
        
        except ValueError:
            print("ID должен быть числом")
        except Exception as e:
            print(f"Ошибка: {e}")

########################################################################################################################
    def manage_masters(self):
        """Управление мастерами (админ)"""
        master_service = MasterService(self.session)
        specialty_service = SpecialtyService(self.session)
        
        while True:
            print("\n" + "=" * 40)
            print("УПРАВЛЕНИЕ МАСТЕРАМИ")
            print("=" * 40)
            print("1. Показать всех мастеров")
            print("2. Добавить мастера")
            print("3. Удалить мастера")
            print("4. Найти мастера по ID")
            print("5. Найти мастеров по специальности")
            print("6. Добавить категорию мастеру")
            print("7. Удалить категорию мастеру")
            print("0. Назад в меню администратора")
            print("-" * 40)
            
            choice = input("Выберите действие: ").strip()
            
            if choice == "1":
                masters = master_service.get_all_masters()
                if masters:
                    MasterUI.show_masters_list(masters)
                else:
                    print("Мастера не найдены")
            
            elif choice == "2":
                self.add_master_admin(master_service)
            
            elif choice == "3":
                try:
                    master_id = int(input("Введите ID мастера для удаления: ").strip())
                    master = master_service.get_master_by_id(master_id)
                    
                    if master:
                        MasterUI.show_master_details(master)
                        confirm = input("\nВы уверены что хотите удалить этого мастера? (да/нет): ").lower()
                        if confirm == "да":
                            success = master_service.delete_master(master_id)
                            MasterUI.show_master_deleted(master_id, success)
                        else:
                            print("Удаление отменено")
                    else:
                        print(f"Мастер с ID {master_id} не найден")
                except ValueError:
                    print("ID должен быть числом")
                except MasterError as e:
                    print(f"Ошибка: {e}")
            
            elif choice == "4":
                try:
                    master_id = int(input("Введите ID мастера: ").strip())
                    master = master_service.get_master_by_id(master_id)
                    
                    if master:
                        MasterUI.show_master_details(master)
                    else:
                        print(f"Мастер с ID {master_id} не найден")
                except ValueError:
                    print("ID должен быть числом")
            
            elif choice == "5":
                self.find_masters_by_specialty_admin(specialty_service)

            elif choice == "6":
                print("\n" + "=" * 40)
                print("ДОБАВЛЕНИЕ КАТЕГОРИЙ МАСТЕРУ")
                print("=" * 40)
                master_id = input("Введите id мастера: ")
                self.add_categories_to_master_admin(master_service, master_id)

            elif choice == "7":
                self.remove_category_from_master_admin(master_service)
            
            elif choice == "0":
                break
            
            else:
                print("Неверный выбор.")
    
    def add_master_admin(self, master_service):
        """Добавление мастера администратором"""
        print("\n" + "=" * 40)
        print("ДОБАВЛЕНИЕ НОВОГО МАСТЕРА")
        print("=" * 40)
        
        try:
            first_name = input("Имя мастера: ").strip()
            last_name = input("Фамилия мастера: ").strip()
            phone = input("Телефон мастера: ").strip()
            email = input("Email мастера (необязательно): ").strip()
            specialty = input("Специальность: ").strip()
            
            if not first_name or not last_name or not specialty:
                print("Имя, фамилия и специальность обязательны!")
                return
            
            master = master_service.create_master(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email,
                specialty=specialty,
                category_ids=None
            )
            
            MasterUI.show_master_created(master)
            self.add_categories_to_master_admin(master_service, master.master_id)

        except MasterError as e:
            print(f"Ошибка: {e}")
        
    
    def add_categories_to_master_admin(self, master_service, master_id):
        """Добавление категорий мастеру"""
        category_service = CategoryService(self.session)
        
        categories = category_service.get_all_categories()
        
        print("Доступные категории:")
        CategoryUI.show_all_categories(categories)
        
        print("\nВведите ID категорий через запятую (например: 1,3,5)")
        
        try:
            choices = input("Выберите категории: ").strip()
            category_ids = [int(cat_id.strip()) for cat_id in choices.split(',')]
            
            master_service.add_categories_to_master(master_id, category_ids)
            print(f"Категории успешно добавлены мастеру!")
            
        except ValueError as e:
            print(f"Неверный формат ввода: {e}")
        except ServiceError as e:
            print(f"Ошибка при добавлении категорий: {e}")
    
    def find_masters_by_specialty_admin(self, specialty_service):
        """Поиск мастеров по специальности (админ)"""
        specialties = specialty_service.get_all_specialties()
        if not specialties:
            print("Специальности не найдены")
            return
        
        print("\nДоступные специальности:")
        SpecialtyUI.show_all_specialties(specialties)
        
        try:
            choice = int(input("\nВыберите номер специальности: ").strip())
            if 1 <= choice <= len(specialties):
                selected_specialty = specialties[choice - 1]
                masters = specialty_service.get_masters_by_specialty(selected_specialty)
                
                if masters:
                    SpecialtyUI.show_masters_by_specialty(selected_specialty, masters)
                else:
                    print(f"Мастеров со специальностью '{selected_specialty}' не найдено")
            else:
                print("Неверный номер специальности")
        except ValueError:
            print("Введите число")

    def remove_category_from_master_admin(self, master_service):
        """Удаление категории у мастера"""
        print("\n" + "=" * 40)
        print("УДАЛЕНИЕ КАТЕГОРИИ У МАСТЕРА")
        print("=" * 40)
        
        masters = master_service.get_all_masters()
        if not masters:
            print("Мастера не найдены")
            return
        
        try:
            master_id = int(input("\nВведите ID мастера: ").strip())
            master = master_service.get_master_by_id(master_id)
            
            if not master:
                print(f"Мастер с ID {master_id} не найден")
                return
            
            print(f"\nМастер: {master.full_name}")
            print("Текущие категории:")
            
            if not master.service_categories:
                print("У мастера нет категорий")
                return
            
            i = 1
            for category in master.service_categories:
                print(f"{i}. {category.category_name} (ID: {category.category_id})")
                i += 1
            
            category_choice = int(input("\nВыберите номер категории для удаления: ").strip())
            if not (1 <= category_choice <= len(master.service_categories)):
                print("Неверный номер категории")
                return
            
            selected_category = master.service_categories[category_choice - 1]
            success = master_service.remove_category_from_master(master_id, selected_category.category_id)
            
            if success:
                print(f"Категория '{selected_category.category_name}' удалена у мастера {master.full_name}")
            else:
                print("Не удалось удалить категорию")
        
        except ValueError:
            print("Неверный формат ввода")
        except MasterError as e:
            print(f"Ошибка: {e}")

#######################################################################################################################

    def manage_schedule(self):
        """Управление расписанием (админ)"""
        schedule_service = ScheduleService(self.session)
        master_service = MasterService(self.session)
        appointment_service = AppointmentService(self.session)
        
        while True:
            print("\n" + "=" * 40)
            print("УПРАВЛЕНИЕ РАСПИСАНИЕМ")
            print("=" * 40)
            print("1. Просмотреть расписание мастера")
            print("2. Добавить рабочий день мастеру")
            print("3. Добавить перерыв мастеру")
            print("4. Удалить рабочий день мастера")
            print("5. Удалить перерыв мастера")
            print("6. Просмотреть занятые слоты мастера")
            print("7. Массовое добавление расписания")
            print("0. Назад в меню администратора")
            print("-" * 40)
            
            choice = input("Выберите действие: ").strip()
            
            if choice == "1":
                self.view_master_schedule(schedule_service, master_service, appointment_service)
            
            elif choice == "2":
                self.add_working_day(schedule_service, master_service)
            
            elif choice == "3":
                self.add_break_to_master(schedule_service, master_service)
            
            elif choice == "4":
                self.remove_working_day(schedule_service, master_service)
            
            elif choice == "5":
                self.remove_master_break(schedule_service, master_service)
            
            elif choice == "6":
                self.view_booked_slots(appointment_service, master_service)

            elif choice == "7":
                self.massive_add_schedule(schedule_service, master_service)
            
            elif choice == "0":
                break
            
            else:
                print("Неверный выбор.")
    
    def view_master_schedule(self, schedule_service, master_service, appointment_service):
        """Просмотр расписания мастера"""
        print("\n" + "=" * 40)
        print("ПРОСМОТР РАСПИСАНИЯ МАСТЕРА")
        print("=" * 40)
        
        masters = master_service.get_all_masters()
        if not masters:
            print("Мастера не найдены")
            return
        
        print("Доступные мастера:")
        MasterUI.show_masters_list(masters)
        
        try:
            master_id = int(input("\nВведите ID мастера: ").strip())
            master = master_service.get_master_by_id(master_id)
            
            if not master:
                print(f"Мастер с ID {master_id} не найден")
                return
            
            date_str = input("Введите дату (ДД.ММ.ГГГГ) (оставьте пустым для сегодня): ").strip()
            
            if date_str:
                work_date = datetime.strptime(date_str, "%d.%m.%Y").date()
            else:
                work_date = date.today()
            
            schedule = schedule_service.get_schedule_by_date(master_id, work_date)
            
            if schedule:
                appointments = appointment_service.get_master_appointments(master_id, work_date)
                ScheduleUI.show_schedule_details(schedule, appointments)
            else:
                print(f"У мастера {master.full_name} нет расписания на {work_date}")
            
        except ValueError as e:
            print(f"Ошибка ввода: {e}")
    
    def add_working_day(self, schedule_service, master_service):
        """Добавление рабочего дня мастеру"""
        print("\n" + "=" * 40)
        print("ДОБАВЛЕНИЕ РАБОЧЕГО ДНЯ")
        print("=" * 40)
        
        masters = master_service.get_all_masters()
        if not masters:
            print("Мастера не найдены")
            return
        
        print("Доступные мастера:")
        MasterUI.show_masters_list(masters)
        
        try:
            master_id = int(input("\nВведите ID мастера: ").strip())
            master = master_service.get_master_by_id(master_id)
            
            if not master:
                print(f"Мастер с ID {master_id} не найден")
                return
            
            date_str = input("Дата (ДД.ММ.ГГГГ): ").strip()
            start_time_str = input("Время начала работы (ЧЧ:ММ): ").strip()
            end_time_str = input("Время окончания работы (ЧЧ:ММ): ").strip()
            
            work_date = datetime.strptime(date_str, "%d.%m.%Y").date()
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
            
            if start_time >= end_time:
                print("Время начала должно быть раньше времени окончания!")
                return
            
            schedule = schedule_service.add_work_day(master_id, work_date, start_time, end_time)
            ScheduleUI.show_schedule_created(schedule)
            
        except ValueError as e:
            print(f"Ошибка ввода формата: {e}")
        except ScheduleError as e:
            print(f"Ошибка: {e}")
    
    def add_break_to_master(self, schedule_service, master_service):
        """Добавление перерыва мастеру"""
        print("\n" + "=" * 40)
        print("ДОБАВЛЕНИЕ ПЕРЕРЫВА МАСТЕРУ")
        print("=" * 40)
        
        masters = master_service.get_all_masters()
        if not masters:
            print("Мастера не найдены")
            return
        
        print("Доступные мастера:")
        MasterUI.show_masters_list(masters)
        
        try:
            master_id = int(input("\nВведите ID мастера: ").strip())
            master = master_service.get_master_by_id(master_id)
            
            if not master:
                print(f"Мастер с ID {master_id} не найден")
                return
            
            date_str = input("Дата расписания (ДД.ММ.ГГГГ): ").strip()
            work_date = datetime.strptime(date_str, "%d.%m.%Y").date()
            
            schedule = schedule_service.get_schedule_by_date(master_id, work_date)
            if not schedule:
                print(f"У мастера нет расписания на {date_str}")
                return
            
            if schedule.is_day_off:#type: ignore
                print(f"{date_str} - выходной день у мастера")
                return
            
            print(f"\nТекущее расписание: {schedule.work_hours}")
            
            if schedule.breaks:
                print("Существующие перерывы:")
                i = 1
                for master_break in schedule.breaks:
                    print(f"{i}) {master_break.break_start} - {master_break.break_end} - ({master_break.reason})" if master_break.reason else "")#type: ignore
                    i += 1
            
            break_start_str = input("\nНачало перерыва (ЧЧ:ММ): ").strip()
            break_end_str = input("Конец перерыва (ЧЧ:ММ): ").strip()
            reason = input("Причина перерыва (необязательно): ").strip()
            
            break_start = datetime.strptime(break_start_str, "%H:%M").time()
            break_end = datetime.strptime(break_end_str, "%H:%M").time()
            
            master_break = schedule_service.add_break(
                schedule_id=schedule.schedule_id,#type: ignore
                break_start=break_start,
                break_end=break_end,
                reason=reason
            )
            
            ScheduleUI.show_break_created(master_break)
            
        except ValueError as e:
            print(f"Ошибка ввода формата: {e}")
        except ScheduleError as e:
            print(f"Ошибка: {e}")
    
    def remove_working_day(self, schedule_service, master_service):
        """Удаление рабочего дня мастера"""
        print("\n" + "=" * 40)
        print("УДАЛЕНИЕ РАБОЧЕГО ДНЯ")
        print("=" * 40)
        
        masters = master_service.get_all_masters()
        if not masters:
            print("Мастера не найдены")
            return
        
        print("Доступные мастера:")
        MasterUI.show_masters_list(masters)
        
        try:
            master_id = int(input("\nВведите ID мастера: ").strip())
            master = master_service.get_master_by_id(master_id)
            
            if not master:
                print(f"Мастер с ID {master_id} не найден")
                return
            
            date_str = input("Дата для удаления (ДД.ММ.ГГГГ): ").strip()
            work_date = datetime.strptime(date_str, "%d.%m.%Y").date()
            
            schedule = schedule_service.get_schedule_by_date(master_id, work_date)
            if not schedule:
                print(f"У мастера нет расписания на {date_str}")
                return
            
            from management.schedule_management import AppointmentService
            appointment_service = AppointmentService(self.session)
            appointments = appointment_service.get_master_appointments(master_id, work_date)
            
            if appointments:
                print(f"На {date_str} есть записи:")
                AppointmentUI.show_appointment_list(appointments)
                confirm = input("\nУдаление расписания отменит все записи. Продолжить? (да/нет): ").lower()
                if confirm == "нет":
                    print("Удаление отменено")
                    return
            
            self.session.delete(schedule)
            self.session.commit()
            print(f"Расписание на {date_str} удалено")
            
        except ValueError as e:
            print(f"Ошибка ввода формата: {e}")
        
    def remove_master_break(self, schedule_service, master_service):
        """Удаление перерыва мастера"""
        print("\n" + "=" * 40)
        print("УДАЛЕНИЕ ПЕРЕРЫВА")
        print("=" * 40)
        
        masters = master_service.get_all_masters()
        if not masters:
            print("Мастера не найдены")
            return
        
        print("Доступные мастера:")
        MasterUI.show_masters_list(masters)
        
        try:
            master_id = int(input("\nВведите ID мастера: ").strip())
            master = master_service.get_master_by_id(master_id)
            
            if not master:
                print(f"Мастер с ID {master_id} не найден")
                return
            
            date_str = input("Дата расписания (ДД.ММ.ГГГГ): ").strip()
            work_date = datetime.strptime(date_str, "%d.%m.%Y").date()
            
            schedule = schedule_service.get_schedule_by_date(master_id, work_date)
            if not schedule:
                print(f"У мастера нет расписания на {date_str}")
                return
            
            if schedule.is_day_off:#type: ignore
                print(f"{date_str} - выходной день у мастера")
                return
            
            if not schedule.breaks:
                print(f"У мастера нет перерывов на {date_str}")
                return
            
            print(f"\nТекущее расписание: {schedule.work_hours}")
            print(f"Перерывы на {date_str}:")
            
            i = 1
            for master_break in schedule.breaks:
                print(f"{i}) {master_break.break_start} - {master_break.break_end}" + 
                      (f" ({master_break.reason})" if master_break.reason else ""))#type: ignore
                i += 1
            
            try:
                break_choice = int(input("\nВыберите номер перерыва для удаления: ").strip())
                if not (1 <= break_choice <= len(schedule.breaks)):
                    print("Неверный номер перерыва")
                    return
                
                selected_break = schedule.breaks[break_choice - 1]
                
                success = schedule_service.remove_break(selected_break.break_id)#type: ignore
                if success:
                    print(f"Перерыв {selected_break.break_start} - {selected_break.break_end} удален")
                else:
                    print("Не удалось удалить перерыв")

            
            except ValueError:
                print("Неверный ввод. Введите число")
        
        except ValueError as e:
            print(f"Ошибка ввода формата даты: {e}")
        except ScheduleError as e:
            print(f"Ошибка: {e}")
    
    def view_booked_slots(self, appointment_service, master_service):
        """Просмотр занятых слотов мастера"""
        print("\n" + "=" * 40)
        print("ЗАНЯТЫЕ СЛОТЫ МАСТЕРА")
        print("=" * 40)
        
        masters = master_service.get_all_masters()
        if not masters:
            print("Мастера не найдены")
            return
        
        print("Доступные мастера:")
        MasterUI.show_masters_list(masters)
        
        try:
            master_id = int(input("\nВведите ID мастера: ").strip())
            master = master_service.get_master_by_id(master_id)
            
            if not master:
                print(f"Мастер с ID {master_id} не найден")
                return
            
            date_str = input("Дата (ДД.ММ.ГГГГ): ").strip()
            target_date = datetime.strptime(date_str, "%d.%m.%Y").date()
            
            appointments = appointment_service.get_master_appointments(master_id, target_date)
            
            if appointments:
                print(f"\nЗанятые слоты мастера {master.full_name} на {date_str}:")
                AppointmentUI.show_appointment_list(appointments)
            else:
                print(f"У мастера {master.full_name} нет записей на {date_str}")
            
        except ValueError as e:
            print(f"Ошибка ввода: {e}")
    
    def massive_add_schedule(self, schedule_service, master_service):
        """Массовое добавление расписания"""
        print("\n" + "=" * 40)
        print("МАССОВОЕ ДОБАВЛЕНИЕ РАСПИСАНИЯ")
        print("=" * 40)
        
        masters = master_service.get_all_masters()
        if not masters:
            print("Мастера не найдены")
            return
        
        print("Доступные мастера:")
        MasterUI.show_masters_list(masters)
        
        try:
            master_id = int(input("\nВведите ID мастера: ").strip())
            master = master_service.get_master_by_id(master_id)
            
            if not master:
                print(f"Мастер с ID {master_id} не найден")
                return
            
            print(f"\nМастер: {master.full_name}")
            print()
            
            start_date_str = input("Начальная дата (ДД.ММ.ГГГГ): ").strip()
            end_date_str = input("Конечная дата (ДД.ММ.ГГГГ): ").strip()
            
            start_date = datetime.strptime(start_date_str, "%d.%m.%Y").date()
            end_date = datetime.strptime(end_date_str, "%d.%m.%Y").date()
            
            print("\nВведите рабочие часы:")
            start_time_str = input("Время начала (ЧЧ:ММ): ").strip()
            end_time_str = input("Время окончания (ЧЧ:ММ): ").strip()
            
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
            
            print("\nВыберите дни недели:")
            print("1. Все дни")
            print("2. Выбрать конкретные дни")
            
            days_choice = input("Ваш выбор (1-2): ").strip()
            
            weekdays = None
            
            if days_choice == "1":
                weekdays = None
                days_desc = "все дни"
            elif days_choice == "2":
                print("\nВыберите дни (вводите номера через запятую):")
                print("0 - Понедельник")
                print("1 - Вторник")
                print("2 - Среда")
                print("3 - Четверг")
                print("4 - Пятница")
                print("5 - Суббота")
                print("6 - Воскресенье")
                
                days_input = input("Номера дней: ").strip()
                weekdays = [int(d.strip()) for d in days_input.split(',')]
                
                for day in weekdays:
                    if day < 0 or day > 6:
                        print(f"Неверный номер дня: {day}")
                        return
                
                weekdays.sort()
            else:
                print("Неверный выбор")
                return
            created_schedules = schedule_service.bulk_add_schedule(master_id=master_id, start_date=start_date, end_date=end_date,
                                                                       start_time=start_time, end_time=end_time, weekdays=weekdays)
                
            if created_schedules:
                print("\nРасписание добавлено на даты:")
                for schedule in created_schedules:
                    days_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
                    weekday_name = days_names[schedule.work_date.weekday()] #type: ignore
                    print(f"- {schedule.work_date.strftime('%d.%m.%Y')} ({weekday_name})")
            else:
                print("Расписание не добавлено")
        
        except ValueError as e:
            print(f"Ошибка ввода формата: {e}")

##############################################################################################################################

    def manage_appointments(self):
        """Управление записями (админ)"""
        appointment_service = AppointmentService(self.session)
        master_service = MasterService(self.session)
        client_service = ClientService(self.session)
        schedule_service = ScheduleService(self.session)
        service_service = ServiceService(self.session)
        
        while True:
            print("\n" + "=" * 40)
            print("УПРАВЛЕНИЕ ЗАПИСЯМИ")
            print("=" * 40)
            print("1. Просмотреть все записи")
            print("2. Найти запись по ID")
            print("3. Найти записи клиента")
            print("4. Найти записи мастера")
            print("5. Создать запись для клиента")
            print("6. Отменить запись")
            print("7. Изменить статус записи")
            print("8. Добавить заметку к записи")
            print("0. Назад в меню администратора")
            print()
            
            choice = input("Выберите действие: ").strip()
            
            if choice == "1":
                self.view_all_appointments(appointment_service)
            
            elif choice == "2":
                self.find_appointment_by_id(appointment_service)
            
            elif choice == "3":
                self.find_client_appointments(appointment_service, client_service)
            
            elif choice == "4":
                self.find_master_appointments(appointment_service, master_service)
            
            elif choice == "5":
                self.create_appointment_admin(appointment_service, client_service, 
                                            master_service, schedule_service, service_service)
            
            elif choice == "6":
                self.cancel_appointment_admin(appointment_service)
            
            elif choice == "7":
                self.change_appointment_status(appointment_service)
            
            elif choice == "8":
                self.add_note_to_appointment(appointment_service)
            
            elif choice == "0":
                break
            
            else:
                print("Неверный выбор.")
    
    def view_all_appointments(self, appointment_service):
        """Просмотр всех записей с фильтрами"""
        print("\n" + "=" * 40)
        print("ПРОСМОТР ВСЕХ ЗАПИСЕЙ")
        print("=" * 40)
        
        print("\nФильтры:")
        print("1. Все записи")
        print("2. Только запланированные")
        print("3. Только выполненные")
        print("4. Только отмененные")
        print("5. Только неявки")
        
        try:
            filter_choice = input("Выберите фильтр (1-5): ").strip()
            
            status_filter = None
            if filter_choice == "2":
                status_filter = AppointmentStatus.SCHEDULED
            elif filter_choice == "3":
                status_filter = AppointmentStatus.COMPLETED
            elif filter_choice == "4":
                status_filter = AppointmentStatus.CANCELLED
            elif filter_choice == "5":
                status_filter = AppointmentStatus.NO_SHOW
            elif filter_choice != "1":
                print("Неверный выбор фильтра")
                return
            
            date_filter = input("Дата (ДД.ММ.ГГГГ) или оставьте пустым для всех: ").strip()
            target_date = None
            if date_filter:
                target_date = datetime.strptime(date_filter, "%d.%m.%Y").date()
            
            appointments = appointment_service.get_all_appointments(
                status=status_filter,
                start_date=target_date,
                end_date=target_date
            )
            
            if appointments:
                AppointmentUI.show_appointment_list(appointments)
            else:
                print("Записи не найдены")
        
        except ValueError as e:
            print(f"Ошибка формата даты: {e}")
    
    def find_appointment_by_id(self, appointment_service):
        """Поиск записи по ID"""
        print("\n" + "=" * 40)
        print("ПОИСК ЗАПИСИ ПО ID")
        print("=" * 40)
        
        try:
            appointment_id = int(input("Введите ID записи: ").strip())
            from models.schedule import Appointment
            appointment = self.session.query(Appointment).filter_by(appointment_id=appointment_id).first()
            
            if appointment:
                AppointmentUI.show_appointment_details(appointment)
            else:
                print(f"Запись с ID {appointment_id} не найдена")
        
        except ValueError:
            print("ID должен быть числом")
    
    def find_client_appointments(self, appointment_service, client_service):
        """Поиск записей клиента по телефону"""
        print("\n" + "=" * 40)
        print("ПОИСК ЗАПИСЕЙ КЛИЕНТА ПО ТЕЛЕФОНУ")
        print("=" * 40)
        
        try:
            phone = input("Введите телефон клиента: ").strip()
            client = client_service.get_client_by_phone(phone)
            
            if not client:
                print(f"Клиент с телефоном {phone} не найден")
                return
            
            print(f"\nКлиент: {client.full_name} (ID: {client.client_id})")
            
            appointments = appointment_service.get_client_appointments(client.client_id, None)
            
            if appointments:
                AppointmentUI.show_appointment_list(appointments)
            else:
                print("У клиента нет записей")
        
        except ScheduleError as e:
            print(f"Ошибка: {e}")

    
    def find_master_appointments(self, appointment_service, master_service):
        """Поиск записей мастера"""
        print("\n" + "=" * 40)
        print("ПОИСК ЗАПИСЕЙ МАСТЕРА")
        print("=" * 40)
        
        masters = master_service.get_all_masters()
        if not masters:
            print("Мастера не найдены")
            return
        
        print("Доступные мастера:")
        MasterUI.show_masters_list(masters)
        
        try:
            master_id = int(input("\nВведите ID мастера: ").strip())
            master = master_service.get_master_by_id(master_id)
            
            if not master:
                print(f"Мастер с ID {master_id} не найден")
                return
            
            date_filter = input("Дата (ДД.ММ.ГГГГ) или оставьте пустым для всех: ").strip()
            target_date = None
            if date_filter:
                target_date = datetime.strptime(date_filter, "%d.%m.%Y").date()
            
            appointments = appointment_service.get_master_appointments(master_id, target_date)
            
            if appointments:
                AppointmentUI.show_appointment_list(appointments)
            else:
                print(f"У мастера {master.full_name} нет записей" + 
                      (f" на {date_filter}" if date_filter else ""))
        
        except ValueError as e:
            print(f"Ошибка формата: {e}")
    
    def create_appointment_admin(self, appointment_service, client_service, 
                              master_service, schedule_service, service_service):
        """Создание записи для клиента администратором"""
        print("\n" + "=" * 40)
        print("СОЗДАНИЕ ЗАПИСИ ДЛЯ КЛИЕНТА")
        print("=" * 40)
    
        try:
            # 1. client
            phone = input("Телефон клиента: ").strip()
            client = client_service.get_client_by_phone(phone)
            if not client:
                print(f"Клиент с телефоном {phone} не найден")
                return
            print(f"Клиент: {client.full_name} (ID: {client.client_id})")

            # 2. service
            services = service_service.get_all_services()
            if not services:
                print("Нет доступных услуг")
                return
            print("\nДоступные услуги:")
            ServiceUI.show_services_list(services)
            service_id = int(input("\nID услуги: ").strip())
            service = service_service.get_service_by_id(service_id)
            if not service:
                print(f"Услуга с ID {service_id} не найдена")
                return
            print(f"Услуга: {service.service_name} ({service.good_format_time}, {service.price} руб.)")
        
            # 3. date
            date_str = input("Дата записи (ДД.ММ.ГГГГ): ").strip()
            work_date = datetime.strptime(date_str, "%d.%m.%Y").date()
            #if work_date < date.today():
            #    print("Нельзя создавать записи на прошедшие даты")
            #    return
        
            # 4. masters 
            all_masters = master_service.get_all_masters()
            suitable_masters = []
        
            for master in all_masters:
                if not any(cat.category_id == service.category_id for cat in master.service_categories):
                    continue
            
                schedule = schedule_service.get_schedule_by_date(master.master_id, work_date)
                if not schedule:
                    continue

                time_slots = schedule_service.get_available_time_slots(schedule_id=schedule.schedule_id, service_duration=service.duration_minutes)#type: ignore
                if not time_slots:
                    continue
            
                suitable_masters.append(master)
        
            if not suitable_masters:
                print(f"Нет доступных мастеров для услуги '{service.service_name}' на {date_str}")
                return
        
            print(f"\nМастера, доступные для '{service.service_name}' на {date_str}:")
            i = 1
            for master in suitable_masters:
                print(f"{i}. {master.full_name} - {master.specialty}")
                i += 1
    
            # 5. master choice
            master_choice = int(input("\nВыберите номер мастера: ").strip())
            if not (1 <= master_choice <= len(suitable_masters)):
                print("Неверный номер мастера")
                return
    
            selected_master = suitable_masters[master_choice - 1]
            master_id = selected_master.master_id
        
            schedule = schedule_service.get_schedule_by_date(master_id, work_date)
            time_slots = schedule_service.get_available_time_slots(schedule_id=schedule.schedule_id, service_duration=service.duration_minutes)#type: ignore

            print(f"\nДоступные слоты у мастера {selected_master.full_name} на {date_str}:")
            i = 1
            for slot in time_slots:
                print(f"{i}) {slot.strftime('%H:%M')}")
                i += 1
        
            # 6. time choice
            time_choice = int(input("\nВыберите номер слота: ").strip())
            if not (1 <= time_choice <= len(time_slots)):
                print("Неверный номер слота")
                return
        
            start_datetime = time_slots[time_choice - 1]
    
            # 7. notes
            notes = input("Заметки (необязательно): ").strip()

            # 8. making an appointment
            appointment = appointment_service.create_appointment(client_id=client.client_id, service_id=service_id, schedule_id=schedule.schedule_id,#type: ignore
                                                             start_datetime=start_datetime, notes=notes)
            
            if appointment:
                AppointmentUI.show_appointment_created(appointment)
            else:
                print("Не удалось создать запись")
    
        except ValueError as e:
            print(f"Ошибка ввода: {e}")
        except ScheduleError as e:
            print(f"Ошибка: {e}")
    
    def cancel_appointment_admin(self, appointment_service):
        """Отмена записи администратором"""
        print("\n" + "=" * 40)
        print("ОТМЕНА ЗАПИСИ")
        print("=" * 40)
        
        try:
            appointment_id = int(input("Введите ID записи для отмены: ").strip())
            
            appointment = self.session.query(Appointment).filter_by(appointment_id=appointment_id).first()
            if not appointment:
                print(f"Запись с ID {appointment_id} не найдена")
                return
            
            AppointmentUI.show_appointment_details(appointment)
            
            success = appointment_service.admin_cancel_appointment(appointment_id)
            AppointmentUI.show_appointment_cancelled(appointment_id, success, by_client=False)

        except ValueError:
            print("ID должен быть числом")
        except ScheduleError as e:
            print(f"Ошибка: {e}")
    
    def change_appointment_status(self, appointment_service):
        """Изменение статуса записи"""
        print("\n" + "=" * 40)
        print("ИЗМЕНЕНИЕ СТАТУСА ЗАПИСИ")
        print("=" * 40)
        
        try:
            appointment_id = int(input("Введите ID записи: ").strip())
            appointment = self.session.query(Appointment).filter_by(appointment_id=appointment_id).first()
            if not appointment:
                print(f"Запись с ID {appointment_id} не найдена")
                return
            AppointmentUI.show_appointment_details(appointment)
            
            print("\nВСЕ СТАТУСЫ ЗАПИСИ:")
            print("1. SCHEDULED - Запланировано")
            print("2. COMPLETED - Выполнено")
            print("3. CANCELLED - Отменено")
            print("4. NO_SHOW - Неявка")
            
            status_map = {"1": AppointmentStatus.SCHEDULED, "2": AppointmentStatus.COMPLETED,
                          "3": AppointmentStatus.CANCELLED, "4": AppointmentStatus.NO_SHOW}
            
            choice = input("\nВыберите новый статус (1-4): ").strip()
            
            if choice not in status_map:
                print("Неверный выбор")
                return
            
            selected_status = status_map[choice]
            current_status = appointment.status
            
            try:
                success = appointment_service.update_appointment_status(appointment_id, selected_status)
                
                if success:
                    print(f"Статус изменен с {current_status.value} на {selected_status.value}")

                    if selected_status == AppointmentStatus.COMPLETED:
                        confirm = input("Вы уверены, что хотите извенить статус на ВЫПОЛНЕНО? (да/нет) ")
                        if confirm.lower().strip() == "да":
                            try:
                                purchase_service = PurchaseService(self.session)
                            
                                amount = float(appointment.service.price)
                                client, discounted_amount, old_level, new_level = purchase_service.add_purchase(appointment.client_id, amount) #type: ignore
                              
                                PurchaseUI.show_purchase_result(client, discounted_amount, old_level, new_level)
                             
                            except Exception as e:
                                print(f"Не удалось добавить покупку: {e}")              
                else:
                    print("Не удалось изменить статус")
            
            except Exception as e:
                print(f"Ошибка при изменении статуса: {e}")
        
        except ValueError:
            print("ID должен быть числом")
        except Exception as e:
            print(f"Ошибка: {e}")
    
    def add_note_to_appointment(self, appointment_service):
        """Добавление заметки к записи"""
        print("\n" + "=" * 40)
        print("ДОБАВЛЕНИЕ ЗАМЕТКИ К ЗАПИСИ")
        print("=" * 40)
        
        try:
            appointment_id = int(input("Введите ID записи: ").strip())
            appointment = self.session.query(Appointment).filter_by(appointment_id=appointment_id).first()
            if not appointment:
                print(f"Запись с ID {appointment_id} не найдена")
                return
            
            AppointmentUI.show_appointment_details(appointment)
            
            if appointment.notes: #type: ignore
                print(f"Текущая заметка: {appointment.notes}")
                new_note = input("Введите новую заметку: ").strip()
            else:
                new_note = input("Введите заметку: ").strip()
            
            success = appointment_service.add_note_to_appointment(appointment_id, new_note)
            
            if success:
                print("Заметка обновлена")
            else:
                print("Не удалось обновить заметку")
        
        except ValueError:
            print("ID должен быть числом")
        except ScheduleError as e:
            print(f"Ошибка: {e}")

###############################################################################################################################
    def show_admin_menu(self):
        """Меню администратора"""
        while True:
            print("\n" + "=" * 40)
            print("МЕНЮ АДМИНИСТРАТОРА")
            print("=" * 40)
            print("1. Управление клиентами")
            print("2. Управление мастерами")
            print("3. Управление услугами")
            print("4. Управление расписанием")
            print("5. Управление записями")
            print("6. Статистика салона")
            print("0. Выйти из аккаунта администратора")
            print("-" * 40)
            
            choice = input("Выберите действие: ").strip()
            
            if choice == "1":
                self.manage_clients()
            elif choice == "2":
                self.manage_masters()
            elif choice == "3":
                self.manage_services()
            elif choice == "4":                
                self.manage_schedule()
            elif choice == "5":
                self.manage_appointments()
            elif choice == "6":
                print("\n" + "=" * 50)
                print("📊 СТАТИСТИКА САЛОНА")
                print("=" * 50)
                print("Запуск интерактивного дашборда...")
                print("Откроется в браузере через несколько секунд")
                print("-" * 50)
                
                try:
                    from dashboard import run_statistics_dashboard
                    result = run_statistics_dashboard(self.session)
                    print(result)
                except ImportError as e:
                    print(f"Ошибка: {e}")
                    print("Установите зависимости: pip install dash plotly pandas")
                except Exception as e:
                    print(f"Ошибка запуска: {e}")
                
                print("\nДля продолжения закройте вкладку браузера")
                input("Нажмите Enter чтобы вернуться в меню...")
            elif choice == "0":
                self.is_admin = False
                print("Выход из аккаунта администратора выполнен.")
                break
            else:
                print("Неверный выбор.")


if __name__ == "__main__":
    main_menu = MainMenu(session)
    main_menu.show_main_auth_menu()
