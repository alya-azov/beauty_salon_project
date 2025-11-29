from sqlalchemy.orm import Session
from models.clients import Client
from typing import Optional
from user_interface.client_functions import create_client
import hashlib

# Данные администратора (без хэша)
admin = "admin"
admin_password = "admin123"

# Нормализация телефона
def normalize_phone(phone_str: str) -> str:
    # Удаляем все нецифровые символы 
    cleaned = ''.join(c for c in phone_str if c.isdigit() or c == '+')
        
    # Заменяем 7 на 8 если номер начинается с 7
    if cleaned.startswith('7') or cleaned.startswith('8'):
        cleaned = '+7' + cleaned[1:]
    return cleaned

#для красивого вывода номера
def format_phone(phone_str: str) -> str:
    normalized = normalize_phone(phone_str)
    if len(normalized) == 12 and normalized.startswith('+7'):
        return f"+7 ({normalized[2:5]}) {normalized[5:8]}-{normalized[8:10]}-{normalized[10:]}"
    return normalized
    

# для хэширования
def simple_hash(password: str) -> str:
    return hashlib.md5(password.encode('utf-8')).hexdigest()

# вход для клиента
def login_client(session: Session) -> Optional[Client]:
    print("\nВход для клиента")
    phone = input("Введите телефон: ")
    password = input("Введите пароль: ")

    normalized_phone = normalize_phone(phone)
    
    client = session.query(Client).filter(Client.phone == normalized_phone).first()
    if client and client.password_hash == simple_hash(password): #type: ignore
        print(f"Добро пожаловать, {client.full_name}!")
        return client
    else:
        print("Неверный телефон или пароль")
        return None

# вход для admin
def login_admin() -> bool:
    print("\nВход для администратора")
    username = input("Логин: ")
    password = input("Пароль: ")
    
    if username == admin and password == admin_password:
        print("Добро пожаловать, Администратор!")
        return True
    else:
        print("Неверный логин или пароль")
        return False

# регистрация клиента
def register_client(session: Session) -> Optional[Client]:
    print("\nРегистрация нового клиента")
    
    first_name = input("Имя: ")
    last_name = input("Фамилия: ")
    phone = input("Телефон: ")
    email = input("Email: ")
    password = input("Пароль: ")
    confirm_password = input("Подтвердите пароль: ")
    
    if password != confirm_password:
        print("Пароли не совпадают!")
        return None
    
    #приводим email к нижнему регистру
    normalized_email = email.lower().strip()

    normalized_phone = normalize_phone(phone)
    
    # Проверка на уникальность с нормализованными данными
    existing_client = session.query(Client).filter((Client.email.ilike(normalized_email)) | (Client.phone == normalized_phone)).first()
    
    if existing_client:
        if existing_client.email.lower() == normalized_email: #type: ignore
            print("Клиент с таким email уже существует!")
        else:
            print("Клиент с таким телефоном уже существует!")
        return None

    client = create_client(session, first_name, last_name, normalized_phone, normalized_email, password)
    return client

