import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from admin.service_management import add_service, delete_service, update_service, service_by_id, get_all_services, get_services_by_category, get_all_categories, add_new_category, delete_category
from models.services import Service, ServiceCategory, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def setup_test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

# Создаем услугу
def test_service_creation():
    session = setup_test_db()
    category = ServiceCategory(category_name="маникюр")
    session.add(category)
    session.commit()
    
    service = Service(
        service_name="Маникюр с покрытием",
        duration_minutes=90,
        price="2500",
        category_id=1
    )
    
    assert service.service_name == "Маникюр с покрытием"
    assert service.duration_minutes == 90
    assert service.price == "2500"
    assert service.category_id == 1
    print("test_service_creation")

# формат времени
def test_service_good_format_time():
    service1 = Service(duration_minutes=90)
    assert service1.good_format_time == "1 ч 30 мин"
    
    service2 = Service(duration_minutes=45)
    assert service2.good_format_time == "45 мин"
    
    service3 = Service(duration_minutes=120)
    assert service3.good_format_time == "2 ч 0 мин"
    
    print("test_service_good_format_time")

# удаляем услугу
def test_delete_service_function():
    session = setup_test_db()
    
    category = ServiceCategory(category_name="маникюр")
    session.add(category)
    service = Service(service_name="Маникюр", duration_minutes=90, price="2500", category_id=1)
    session.add(service)
    session.commit()
    
    result = delete_service(session, 1)
    
    assert result is True
    print("test_delete_service_function")

# удаляем несуществующую услугу
def test_delete_service_not_found():
    session = setup_test_db()
    
    result = delete_service(session, 999)
    
    assert result is False
    print("test_delete_service_not_found")

# поиск услуги по id
def test_service_by_id_function():
    session = setup_test_db()
    
    category = ServiceCategory(category_name="маникюр")
    session.add(category)
    service = Service(service_name="я усталь", duration_minutes=90, price="2500", category_id=1)
    session.add(service)
    session.commit()
    
    found_service = service_by_id(session, 1)
    
    assert found_service is not None
    assert found_service.service_name == "я усталь"
    print("test_service_by_id_function")

# Создаем категорию
def test_add_new_category_function():
    session = setup_test_db()
    
    result = add_new_category(session, "массаж")
    assert result is True

    category = session.query(ServiceCategory).filter_by(category_name="массаж").first()
    assert category is not None
    print("test_add_new_category_function")

# Создаем уже существующую категорию
def test_add_existing_category():
    session = setup_test_db()
    
    category = ServiceCategory(category_name="маникюр")
    session.add(category)
    session.commit()
    result = add_new_category(session, "маникюр")
    
    assert result is False
    print("test_add_existing_category")

#удаляем категорию
def test_delete_category_function():
    session = setup_test_db()
    
    category = ServiceCategory(category_name="маникюр")
    session.add(category)
    session.commit()
    result = delete_category(session, 1)
    
    assert result is True
    print("test_delete_category_function")

#удаляем категорию с услугами
def test_delete_category_with_services():
    session = setup_test_db()

    category = ServiceCategory(category_name="маникюр")
    session.add(category)
    service = Service(service_name="Маникюр", duration_minutes=90, price="2500", category_id=1)
    session.add(service)
    session.commit()
    
    result = delete_category(session, 1)
    
    assert result is False
    print("test_delete_category_with_services")


def run_all_tests():
    print("ТЕСТИРУЕМ УСЛУГИ...\n")
    
    test_service_creation()
    test_service_good_format_time()
    test_delete_service_function()
    test_delete_service_not_found()
    test_service_by_id_function()
    test_add_new_category_function()
    test_add_existing_category()
    test_delete_category_function()
    test_delete_category_with_services()

    print ("ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")

if __name__ == "__main__":
    run_all_tests()