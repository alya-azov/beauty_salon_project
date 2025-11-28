import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.authentification import simple_hash, normalize_phone
from models.clients import Client, SalonCard, DiscountLevel, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def test_normalize_phone():
    assert normalize_phone("+7-999-123-45-67") == "89991234567"
    assert normalize_phone("8-999-123-45-67") == "89991234567"
    assert normalize_phone("7 (999) 123 45 67") == "89991234567"
    print("test_normalize_phone")

def test_client_creation():
    client = Client(
        first_name="Анна", 
        last_name="Иванова",
        phone="89991234567",
        email="anna@test.ru",
        password_hash=simple_hash("pass123")
    )
    assert client.full_name == "Анна Иванова"
    assert client.phone == "89991234567"
    print("test_client_creation")

def test_salon_card():
    card = SalonCard()
    
    # Тест скидок
    card.discount_level = DiscountLevel.STANDARD
    assert card.apply_discount(1000) == 1000
    card.discount_level = DiscountLevel.SILVER
    assert card.apply_discount(1000) == 970
    
    # Тест апгрейда
    card.total_spent = 6000
    card.upgrade_level()
    assert card.discount_level == DiscountLevel.SILVER
    print("test_salon_card")

def test_client_functions():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    session = Session()
    
    from client.client_functions import create_client, update_my_info
    
    # Создание клиента
    client = create_client(
        session=session,
        first_name="Мария",
        last_name="Петрова", 
        phone="+7-911-222-33-44",
        email="MARIA@test.ru",
        password="pass123"
    )
    
    print (client.phone)
    assert client.phone == "89112223344"  # Нормализован
    assert client.email == "maria@test.ru"  # Нижний регистр
    
    # Обновление данных
    update_my_info(session, client, 'phone', '+7-922-444-55-66')
    assert client.phone == '89224445566'
    
    session.close()
    print("test_client_functions - ПРОЙДЕН")

def test_admin_functions():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    session = Session()
    
    from client.client_functions import create_client
    from admin.client_management import get_client_by_phone, add_purchase, delete_client
    
    # Создаем клиента для теста
    client = create_client(
        session=session,
        first_name="Ольга",
        last_name="Николаева",
        phone="+7-911-111-11-11", 
        email="test@test.ru",
        password="test123"
    )
    
    # Поиск по телефону
    found = get_client_by_phone(session, "+7-911-111-11-11")
    assert found is not None
    
    # Добавление покупки
    add_purchase(session, client.client_id, 5000)
    assert client.salon_card.total_spent == 5000
    
    # Удаление клиента
    delete_client(session, client.client_id)
    deleted = session.query(Client).filter_by(client_id=client.client_id).first()
    assert deleted is None
    
    session.close()
    print("test_admin_functions")

def test_hash_functions():
    assert simple_hash("test") == simple_hash("test")
    assert simple_hash("test1") != simple_hash("test2")
    print("test_auth_functions")

def run_all_tests():
    test_normalize_phone()
    test_client_creation() 
    test_salon_card()
    test_client_functions()
    test_admin_functions()
    test_hash_functions()
    print("\nВСЕ ТЕСТЫ ПРОЙДЕНЫ!")

if __name__ == "__main__":
    run_all_tests()