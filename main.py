from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models.base import Base

from auth.authentification import login_admin, simple_hash, login_client
from user_interface.Auth_UI import AuthUI, normalize_phone, format_phone

from models import clients
from models import masters
from models import services
from models import schedule

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

# Подключение к базе данных PostgreSQL
engine = create_engine("postgresql://postgres:4321wwee@localhost:5432/salon_project")
Base.metadata.create_all(engine)

# Создание сессии
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
        first_name, last_name, phone, email, password = AuthUI.show_client_registration_prompt()
        try:    
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
            except Exception as e:
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

    def show_client_menu(self):
        """Меню для клиента (заглушка)"""
        
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
                print ("there will be make_an_appointment_menu")
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
            print("6. Просмотр статистики клиента")
            print("7. Просмотр записей клиента")
            print("8. Удаление клиента")
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
                print("\nПросмотр статистики клиента")
                print("Функция в разработке...")
            
            elif choice == "7":
                print("\nПросмотр записей клиента")
                print("Функция в разработке...")

            elif choice == "8":
                self.delete_client_admin(client_service)
            
            elif choice == "0":
                break
            
            else:
                print("Неверный выбор.")
                input("Нажмите Enter чтобы продолжить...")
    
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
        except Exception as e:
            print(f"Ошибка: {e}")

########################################################################################################################


#######################################################################################################################
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
                #self.manage_masters()
                print(" in th futur")
            elif choice == "3":
                self.manage_services()
            elif choice == "4":
                print(" in th futur")
                #self.manage_schedule()
            elif choice == "5":
                print(" in th futur")
                #self.manage_appointments()
            elif choice == "6":
                #self.view_statistics()
                #хочу это как фичу во 2 итерации, графики там всякие
                print(" in th futur")
            elif choice == "0":
                self.is_admin = False
                print("Выход из аккаунта администратора выполнен.")
                break
            else:
                print("Неверный выбор.")



if __name__ == "__main__":
    main_menu = MainMenu(session)
    main_menu.show_main_auth_menu()


    