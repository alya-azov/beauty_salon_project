from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.masters import Base
from auth.authentification import login_client, login_admin, register_client
from admin.master_management import add_master, delete_master, get_all_masters, get_masters_by_specialty, update_master, master_by_id
from admin.service_management import add_service, delete_service, update_service, service_by_id, get_all_services, get_services_by_category, get_all_categories, add_new_category, delete_category
from client.viewing_options import show_all_masters, show_masters_by_specialty, show_all_services, show_services_by_category, show_service_details, show_master_by_id, show_all_categories
from admin.client_management import delete_client
from client.client_functions import update_my_info

# Подключение к базе данных
engine = create_engine("postgresql://postgres:4321wwee@localhost:5432/salon_project")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


# ========== МЕНЮ МАСТЕРОВ ДЛЯ АДМИНА ==========
def admin_masters_menu():
    while True:
        print()
        print("УПРАВЛЕНИЕ МАСТЕРАМИ")
        print("1. Показать всех мастеров")
        print("2. Добавить мастера")
        print("3. Удалить мастера")
        print("4. Найти мастера по ID")
        print("5. Найти мастеров по специальности")
        print("6. Назад")

        choice = input("Выберите действие: ")

        if choice == "1":
            get_all_masters(session)
        elif choice == "2":
            first_name = input("Имя: ")
            last_name = input("Фамилия: ")
            phone = input("Телефон: ")
            email = input("Email: ")
            specialty = input("Специальность: ")
            add_master(session, first_name, last_name, phone, email, specialty)
        elif choice == "3":
            master_id = int(input("Введите ID мастера для удаления: "))
            delete_master(session, master_id)
        elif choice == "4":
            master_id = int(input("Введите ID мастера: "))
            master_by_id(session, master_id)
        elif choice == "5":
            specialty = input("Введите специальность: ")
            get_masters_by_specialty(session, specialty)
        elif choice == "6":
            break
        else:
            print("Неверный выбор")


# ========== МЕНЮ УСЛУГ ДЛЯ АДМИНА ==========
def admin_services_menu():
    while True:
        print()
        print("УПРАВЛЕНИЕ УСЛУГАМИ")
        print("1. Показать все услуги")
        print("2. Добавить услугу")
        print("3. Удалить услугу")
        print("4. Найти услугу по ID")
        print("5. Показать услуги по категории")
        print("6. Показать все категории")
        print("7. Добавить новую категорию")
        print("8. Обновить услугу")
        print("9. Удалить категорию") 
        print("10. Назад")
        
        choice = input("Выберите действие: ")
        
        if choice == "1":
            get_all_services(session)
        elif choice == "2":
            service_name = input("Название услуги: ")
            duration = int(input("Длительность в минутах: "))
            price = int(input("Цена: "))
            category_id = int(input("ID категории: "))
            add_service(session, service_name, duration, price, category_id)
        elif choice == "3":
            service_id = int(input("Введите ID услуги для удаления: "))
            delete_service(session, service_id)
        elif choice == "4":
            service_id = int(input("Введите ID услуги: "))
            service_by_id(session, service_id)
        elif choice == "5":
            get_all_categories(session)
            category_id = int(input("Введите ID категории: "))
            get_services_by_category(session, category_id)
        elif choice == "6":
            get_all_categories(session)
        elif choice == "7":
            category_name = input("Введите название новой категории: ")
            add_new_category(session, category_name)
        elif choice == "8":
            service_id = int(input("Введите ID услуги: "))
            print("Какие данные обновить?")
            print("service_name - название услуги")
            print("duration_minutes - длительность")
            print("price - цена") 
            print("category_id - категория")
            field = input("Поле для обновления: ")
            value = input("Новое значение: ")
            update_service(session, service_id, field, value)
        elif choice == "9":
            get_all_categories(session)
            category_id = int(input("Введите ID категории для удаления: "))
            delete_category(session, category_id)
        elif choice == "10":
            break
        else:
            print("Неверный выбор")


# ========== МЕНЮ АДМИНИСТРАТОРА ==========
def admin_menu():
    while True:
        print("\nПАНЕЛЬ АДМИНИСТРАТОРА")
        print("1. Управление мастерами")
        print("2. Управление услугами")
        print("3. Выйти")
        
        choice = input("Выберите раздел: ")
        
        if choice == "1":
            admin_masters_menu()
        elif choice == "2":
            admin_services_menu()
        elif choice == "3":
            break
        else:
            print("Неверный выбор")


# ========== МЕНЮ КЛИЕНТА ==========
def client_masters_menu():
    while True:
        print("\n НАШИ МАСТЕРЫ")
        print("1. Показать всех мастеров")
        print("2. Найти мастера по ID")
        print("3. Найти мастеров по специальности")
        print("4. Назад")

        choice = input("Выберите действие: ")

        if choice == "1":
            show_all_masters(session)
        elif choice == "2":
            master_id = int(input("Введите ID мастера: "))
            show_master_by_id(session, master_id)
        elif choice == "3":
            specialty = input("Введите специальность: ")
            show_masters_by_specialty(session, specialty)
        elif choice == "4":
            break
        else:
            print("Неверный выбор")

def client_services_menu():
    while True:
        print("\nНАШИ УСЛУГИ")
        print("1. Показать все услуги")
        print("2. Показать услуги по категории")
        print("3. Найти услугу по ID")
        print("4. Показать все категории")
        print("5. Назад")
        
        choice = input("Выберите действие: ")
        
        if choice == "1":
            show_all_services(session)
        elif choice == "2":
            show_all_categories(session)
            category_id = int(input("Введите ID категории: "))
            show_services_by_category(session, category_id)
        elif choice == "3":
            service_id = int(input("Введите ID услуги: "))
            show_service_details(session, service_id)
        elif choice == "4":
            show_all_categories(session)
        elif choice == "5":
            break
        else:
            print("Неверный выбор")

def client_menu(client):
    while True:
        print("\n👋 МЕНЮ КЛИЕНТА")
        print("1. Просмотр мастеров")
        print("2. Просмотр услуг")
        print("3. Выйти")
        
        choice = input("Выберите действие: ")
        
        if choice == "1":
            client_masters_menu()
        elif choice == "2":
            client_services_menu()
        elif choice == "3":
            break
        else:
            print("Неверный выбор")


# ========== ГЛАВНОЕ МЕНЮ ==========
def main():
    print("САЛОН КРАСОТЫ - ВХОД В СИСТЕМУ")
    
    while True:
        print("\n1. Войти как администратор")
        print("2. Войти как клиент") 
        print("3. Зарегистрироваться как клиент")
        print("4. Выйти из программы")
        
        choice = input("Выберите вариант: ")
        
        if choice == "1":
            if login_admin():
                admin_menu()
        elif choice == "2":
            client = login_client(session)
            if client is None:
                print("jkhkh")
            else: 
                field = input("field: ")
                value = input("value: ")
                update_my_info(session, client, field, value)
            #if client:
            #    client_menu(client)
        elif choice == "3":
            client = register_client(session)
        elif choice == "4":
            print("До свидания!")
            break
        else:
            print("Неверный выбор, попробуйте снова")



# ========== ЗАПУСК ПРОГРАММЫ ==========
if __name__ == "__main__":
    main()
    session.close()