from sqlalchemy.orm import Session
from models.clients import Client
from typing import Optional
import hashlib
from user_interface.Auth_UI import AuthUI, normalize_phone, format_phone

# Данные администратора (без хэша)
admin = "admin"
admin_password = "admin123"

# для хэширования
def simple_hash(password: str) -> str:
    return hashlib.md5(password.encode('utf-8')).hexdigest()

# вход для клиента
def login_client(session: Session) -> Optional[Client]:
    try:
        phone, password = AuthUI.show_client_login_prompt()
        
        normalized_phone = normalize_phone(phone)
        
        client = session.query(Client).filter(Client.phone == normalized_phone).first()
        if client and client.password_hash == simple_hash(password): #type: ignore
            AuthUI.show_client_login_success(client)
            return client
        else:
            AuthUI.show_client_login_failed()
            return None
    except Exception as e:
        AuthUI.show_client_login_failed(str(e))
        return None

def login_admin() -> bool:
    try:
        username, password = AuthUI.show_admin_login_prompt()
        
        if username == admin and password == admin_password:
            AuthUI.show_admin_login_success()
            return True
        else:
            AuthUI.show_admin_login_failed()
            return False
    except Exception as e:
        AuthUI.show_admin_login_failed()
        return False

