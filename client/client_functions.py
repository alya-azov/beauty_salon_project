from models.clients import Client, SalonCard, DiscountLevel
from sqlalchemy.orm import Session
from datetime import datetime

# Создание клиента
def create_client(session: Session, first_name: str, last_name: str, phone: str, 
                 email: str, password: str) -> Client:
    
    from auth.authentification import simple_hash
    from auth.authentification import normalize_phone
    new_client = Client(first_name=first_name, last_name=last_name,
                        phone=normalize_phone(phone) ,email=email.lower().strip(), password_hash=simple_hash(password))
    
    session.add(new_client)
    session.flush()
    
    salon_card = SalonCard(client_id=new_client.client_id, discount_level=DiscountLevel.STANDARD,
                           total_spent=0.0,issue_date=datetime.now())
    
    session.add(salon_card)
    session.commit()
    
    print(f"Новый клиент создан: {new_client.full_name} (ID: {new_client.client_id})")
    return new_client

# обновить свои данные (кроме пароля)
def update_my_info(session: Session, client: Client, field: str, value: str) -> bool:
    if field != 'password':
        if field == 'phone':
            from auth.authentification import normalize_phone
            setattr(client, field, normalize_phone(value))
        elif field == 'email':
            setattr(client, field, value.lower().strip())
        else:
            setattr(client, field, value)
        session.commit()
        print("Данные клиента обновлены!")
        return True
    return False

# сменить пароль
def change_password(session: Session, client: Client) -> bool:
    old_password = input("Старый пароль: ")
    current_client = session.query(Client).filter(Client.client_id == client.client_id).first()
    if current_client.password_hash != simple_hash(old_password):#type: ignore
        session.commit()
        print("Неверный старый пароль!")
        return False
    
    new_password = input("Новый пароль: ")
    confirm_password = input("Подтвердите новый пароль: ")
    
    if new_password != confirm_password:
        print("Пароли не совпадают!")
        return False
    return True

#посмотреть свои данные
def view_my_info(client: Client) -> None:
    print("ID: " + str(client.client_id))
    print("Имя: " + client.full_name)
    print("Телефон: " + client.phone)
    print("Email: " + client.email)
    print("Тип скидочной карты: " + client.salon_card.discount_level.value)
    print("Суммарные траты: " + str(client.salon_card.total_spent) + " руб.")
    print()
