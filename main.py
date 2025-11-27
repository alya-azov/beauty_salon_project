from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker  # ✅ orm
from models.masters import Base, Master  # ✅ models.master и Master с большой буквы
from auth.simple_auth import authenticate_user  # ✅ auth.simple_auth
from admin.master_management import (
    add_master,
    delete_master,
    get_all_masters,
    get_masters_by_specialty,
    update_master,
    master_by_id,
)


# Подключение к PostgreSQL
engine = create_engine("postgresql://postgres:4321wwee@localhost:5432/salon_project")
Session = sessionmaker(engine)
session = Session()


# ========== МЕНЮ АДМИНИСТРАТОРА ==========
def admin_menu():
    while True:
        print("\n🔧 ПАНЕЛЬ АДМИНИСТРАТОРА")
        print("1. Показать всех мастеров")
        print("2. Добавить мастера")
        print("3. Удалить мастера")
        print("4. Обновить мастера")
        print("5. Найти мастеров по специальности")
        print("6. Получить данные мастера по id")
        print("7. Выйти")

        choice = input()

        if choice == "1":
            get_all_masters(session)  # Показываем всех мастеров

        elif choice == "2":
            # Собираем данные для нового мастера
            first_name = input("Имя: ")
            last_name = input("Фамилия: ")
            phone = input("Телефон: ")
            email = input("Email: ")
            specialty = input("Специальность: ")

            add_master(session, first_name, last_name, phone, email, specialty)

        elif choice == "3":
            print("Введите id мастера, которого хотите удалить: ")
            master_id = int(input())
            delete_master(session, master_id)

        elif choice == "4":
            print("Введите id мастера, чьи данные нужно обновить")
            master_id = int(input())
            print("Введите аттрибут и новое значение")
            field = input()
            value = input()
            update_master(session, master_id, field, value)

        elif choice == "5":
            # Ищем мастеров по специальности
            specialty = input("Специальность: ")
            get_masters_by_specialty(session, specialty)

        elif choice == "6":
            print("Введите id мастера, чьи данные вы хотите получить")
            master_id = int(input())
            master_by_id(session, master_id)

        elif choice == "7":
            break  # Выходим из меню администратора

        else:
            print("Неверный выбор")


# ========== МЕНЮ КЛИЕНТА ==========
def client_menu():
    while True:
        print("\n👋 МЕНЮ КЛИЕНТА")
        print("1. Показать всех мастеров")
        print("2. Найти мастеров по специальности")
        print("3. Выйти")

        choice = input("Выберите действие: ")

        if choice == "1":
            get_all_masters(session)  # Только просмотр!

        elif choice == "2":
            specialty = input("Введите специальность: ")
            get_masters_by_specialty(session, specialty)  # Только поиск!

        elif choice == "3":
            break  # Выходим из меню клиента

        else:
            print("Неверный выбор")


# ========== ГЛАВНАЯ ФУНКЦИЯ ПРОГРАММЫ ==========
def main():
    """
    Точка входа в программу.
    Здесь пользователь выбирает роль (админ/клиент) для входа.
    """
    print("САЛОН КРАСОТЫ - ВХОД В СИСТЕМУ")

    while True:
        print("\n1. Войти как администратор")
        print("2. Войти как клиент")
        print("3. Выйти из программы")

        choice = input("Выберите вариант: ")

        if choice == "1":
            # АДМИНИСТРАТОР - запрашиваем логин/пароль
            login = input("Логин: ")
            password = input("Пароль: ")

            # Проверяем через нашу систему аутентификации
            if authenticate_user(login, password) == "admin":
                admin_menu()  # Если верно - запускаем меню админа
            else:
                print("Неверный логин или пароль!")

        # КЛИЕНТ
        elif choice == "2":
            login = input("Логин: ")
            password = input("Пароль: ")

            if authenticate_user(login, password) == "client":
                client_menu()
            else:
                print("Неверный логин или пароль!")

        elif choice == "3":
            print("👋 До свидания!")
            break

        else:
            print("Неверный выбор")


# ========== ЗАПУСК ПРОГРАММЫ ==========
if __name__ == "__main__":

    main()

    session.close()
    print("Соединение с базой данных закрыто")
