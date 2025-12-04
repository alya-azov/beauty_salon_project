import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.authentification import simple_hash, normalize_phone
from models.clients import Client, SalonCard, DiscountLevel, Base
from management.client_management import ClientService, PurchaseService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def test_normalize_phone():
    assert normalize_phone("+7-999-123-45-67") == "+79991234567"
    assert normalize_phone("8-999-123-45-67") == "+79991234567"
    assert normalize_phone("7 (999) 123 45 67") == "+79991234567"
    print("test_normalize_phone")

def test_client_creation():
    client = Client(
        first_name="Анна", 
        last_name="Иванова",
        phone=normalize_phone("89991234567"),
        email="anna@tEst.ru   ".lower().strip(),
        password_hash=simple_hash("pass123")
    )
    assert client.full_name == "Анна Иванова"
    assert client.phone == "+79991234567" 
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

def test_client_service():

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    session = Session()
    
    # Создаем сервис
    client_service = ClientService(session)
    
    # Создание клиента через сервис
    client = client_service.create_client(
        first_name="Мария",
        last_name="Петрова", 
        phone="+7-911-222-33-44",
        email="MARIA@test.ru",
        password="pass123"
    )
    
    assert client.phone == "+79112223344" 
    assert client.email == "maria@test.ru"
    
    # Обновление данных через сервис
    updated_client = client_service.update_client(
        client_id=client.client_id,
        field="phone",
        value="+7-922-444-55-66"
    )
    assert updated_client.phone == "+79224445566"
    
    session.close()
    print("test_client_service")

def test_purchase_service():
    """Тест сервиса покупок"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    session = Session()
    
    # Создаем сервисы
    client_service = ClientService(session)
    purchase_service = PurchaseService(session)
    
    # Создаем клиента для теста
    client = client_service.create_client(
        first_name="Ольга",
        last_name="Николаева",
        phone="+7-911-111-11-11", 
        email="test@test.ru",
        password="test123"
    )
    
    # Проверяем поиск по телефону
    found_client = client_service.get_client_by_phone("+7-911-111-11-11")
    assert found_client is not None
    assert found_client.client_id == client.client_id
    
    # Проверяем, что карта создалась
    assert client.salon_card is not None
    assert client.salon_card.discount_level == DiscountLevel.STANDARD
    assert client.salon_card.total_spent == 0.0
    
    # Добавление покупки
    purchase_result = purchase_service.add_purchase(
        client_id=client.client_id,
        amount=5000.0
    )
    
    client, discounted_amount, old_level, new_level = purchase_result
    
    # Проверяем результаты покупки
    assert discounted_amount == 5000.0
    assert old_level == DiscountLevel.STANDARD
    assert new_level == DiscountLevel.SILVER
    assert client.salon_card.total_spent == 5000.0
    
    # Проверяем удаление клиента
    deleted = client_service.delete_client(client.client_id)
    assert deleted is True
    
    # Проверяем что клиент действительно удален
    deleted_client = client_service.get_client_by_id(client.client_id)
    assert deleted_client is None
    
    session.close()
    print("test_purchase_service")

def test_hash_functions():
    assert simple_hash("test") == simple_hash("test")
    assert simple_hash("test1") != simple_hash("test2")
    print("test_auth_functions")

def run_all_tests():
    test_normalize_phone()
    test_client_creation() 
    test_salon_card()
    test_client_service()
    test_purchase_service()
    test_hash_functions()
    print("\nВСЕ ТЕСТЫ ПРОЙДЕНЫ!")

if __name__ == "__main__":
    run_all_tests()