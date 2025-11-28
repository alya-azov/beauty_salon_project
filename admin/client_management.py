from models.clients import Client, SalonCard, DiscountLevel
from sqlalchemy.orm import Session
from typing import Optional, List

# Клиент по id
def get_client_by_id(session: Session, client_id: int) -> Optional[Client]:
    client = session.query(Client).filter(Client.client_id == client_id).first()
    if client:
        print("id: " + str(client.client_id))
        print("Имя: " + client.full_name)
        print("Телефон: " + client.phone)
        print("Email: " + client.email)
        print("Тип скидочной карты: " + client.salon_card.discount_level.value)
        print("Суммарные траты: " + str(client.salon_card.total_spent) + " руб.")
        print()
        return client
    else:
        print("Клиент не найден")
        print()
        return None

# Клиент по номеру телефона
def get_client_by_phone(session: Session, phone: str) -> Optional[Client]:
    from auth.authentification import normalize_phone
    client = session.query(Client).filter(Client.phone == normalize_phone(phone)).first()
    if client:
        print("id: " + str(client.client_id))
        print("Имя: " + client.full_name)
        print("Телефон: " + client.phone)
        print("Email: " + client.email)
        print("Тип скидочной карты: " + client.salon_card.discount_level.value)
        print("Суммарные траты: " + str(client.salon_card.total_spent) + " руб.")
        print()
        return client
    else:
        print("Клиент не найден")
        print()
        return None

# Клиент по e-mail
def get_client_by_email(session: Session, email: str) -> Optional[Client]:
    client = session.query(Client).filter(Client.email == email.lower().strip()).first()
    if client:
        print("id: " + str(client.client_id))
        print("Имя: " + client.full_name)
        print("Телефон: " + client.phone)
        print("Email: " + client.email)
        print("Тип скидочной карты: " + client.salon_card.discount_level.value)
        print("Суммарные траты: " + str(client.salon_card.total_spent) + " руб.")
        print()
        return client
    else:
        print("Клиент не найден")
        print()
        return None

# вывести всех клиентов
def get_all_clients(session: Session) -> List[Client]:
    clients = session.query(Client).all()
    for client in clients:
        print(str(client.client_id) + ") " + client.first_name + " " + client.last_name)
    print()

    return session.query(Client).all()

# добавление покупки
def add_purchase(session: Session, client_id: int, amount: float) -> bool:
    client = get_client_by_id(session, client_id)
    if client and client.salon_card:
        discounted_amount = client.salon_card.apply_discount(amount)
        client.salon_card.total_spent += discounted_amount
        
        old_level = client.salon_card.discount_level
        client.salon_card.upgrade_level()
        new_level = client.salon_card.discount_level
        
        session.commit()
        
        print("Покупка: " + str(discounted_amount) + " руб.")
        print("Всего: " + str(client.salon_card.total_spent) + " руб.")
        print("Уровень: " + new_level.value)
        
        if old_level != new_level:
            print("Уровень повышен до " + new_level.value + "!")
        
        return True
    return False

# удаление клиента
def delete_client(session: Session, client_id: int) -> bool:
    client = get_client_by_id(session, client_id)
    if client:
        session.delete(client)
        session.commit()
        print("Клиент удален!")
        return True
    return False

# смена пароля администратором
def admin_change_client_password(session: Session) -> bool:
    print()
    print("Смена пароля клиента")
    
    client_id = input("ID клиента: ")
    
    # Проверяем что ввели число
    if not client_id.isdigit():
        print("ID должен быть числом!")
        return False
    
    client_id_num = int(client_id)
    client = session.query(Client).filter(Client.client_id == client_id_num).first()
    
    if not client:
        print("Клиент с таким ID не найден!")
        return False
    
    # Запрашиваем новый пароль
    new_password = input("Новый пароль: ")
    confirm_password = input("Подтвердите новый пароль: ")
    
    if new_password != confirm_password:
        print("Пароли не совпадают!")
        return False
    
    # Меняем пароль
    client.password_hash = simple_hash(new_password)#type: ignore
    session.commit()
    print(f"Пароль клиента {client.full_name} успешно изменен!")
    return True