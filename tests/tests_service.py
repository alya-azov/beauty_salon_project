import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from management.service_management import ServiceService, CategoryService
from models.services import Service, ServiceCategory, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from exceptions import ServiceError

def setup_test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

# Создаем услугу через сервис
def test_service_creation():
    session = setup_test_db()
    category_service = CategoryService(session)
    service_service = ServiceService(session)
    
    category = category_service.create_category("маникюр")
    
    service = service_service.create_service(
        service_name="Маникюр с покрытием",
        duration_minutes=90,
        price=2500,
        category_id=category.category_id #type: ignore
    )
    
    assert service.service_name == "Маникюр с покрытием"#type: ignore
    assert service.duration_minutes == 90#type: ignore
    assert service.price == 2500  #type: ignore
    assert service.category_id == category.category_id#type: ignore
    print("test_service_creation passed")

# формат времени
def test_service_good_format_time():
    service1 = Service(duration_minutes=90)
    assert service1.good_format_time == "1 ч 30 мин"
    
    service2 = Service(duration_minutes=45)
    assert service2.good_format_time == "45 мин"
    
    service3 = Service(duration_minutes=120)
    assert service3.good_format_time == "2 ч 0 мин"
    
    print("test_service_good_format_time passed")

# удаляем услугу через сервис
def test_delete_service_function():
    session = setup_test_db()
    category_service = CategoryService(session)
    service_service = ServiceService(session)
    
    category = category_service.create_category("маникюр")
    service = service_service.create_service(
        service_name="Маникюр", 
        duration_minutes=90, 
        price=2500, 
        category_id=category.category_id#type: ignore
    )
    
    result = service_service.delete_service(service.service_id)#type: ignore
    
    assert result is True
    print("test_delete_service_function passed")

# удаляем несуществующую услугу
def test_delete_service_not_found():
    session = setup_test_db()
    service_service = ServiceService(session)
    
    result = service_service.delete_service(999)
    
    assert result is False
    print("test_delete_service_not_found passed")

# поиск услуги по id через сервис
def test_service_by_id_function():
    session = setup_test_db()
    category_service = CategoryService(session)
    service_service = ServiceService(session)
    
    category = category_service.create_category("маникюр")
    service = service_service.create_service(
        service_name="я усталь", 
        duration_minutes=90, 
        price=2500, 
        category_id=category.category_id#type: ignore
    )
    
    found_service = service_service.get_service_by_id(service.service_id)#type: ignore
    
    assert found_service is not None
    assert found_service.service_name == "я усталь"#type: ignore
    print("test_service_by_id_function passed")

# Создаем категорию через сервис
def test_add_new_category_function():
    session = setup_test_db()
    category_service = CategoryService(session)
    
    category = category_service.create_category("массаж")
    
    assert category is not None
    assert category.category_name == "массаж"#type: ignore
    print("test_add_new_category_function passed")

# Создаем уже существующую категорию
def test_add_existing_category():
    session = setup_test_db()
    category_service = CategoryService(session)
    
    category_service.create_category("маникюр")
    
    try:
        category_service.create_category("маникюр")
        assert False, "Должна была быть ошибка"
    except ServiceError as e:
        assert "уже существует" in str(e)
        print("test_add_existing_category passed")

# удаляем категорию через сервис
def test_delete_category_function():
    session = setup_test_db()
    category_service = CategoryService(session)
    
    category = category_service.create_category("маникюр")
    result = category_service.delete_category(category.category_id)#type: ignore
    
    assert result is True
    print("test_delete_category_function passed")

# удаляем категорию с услугами
def test_delete_category_with_services():
    session = setup_test_db()
    category_service = CategoryService(session)
    service_service = ServiceService(session)
    
    category = category_service.create_category("маникюр")
    service_service.create_service(
        service_name="Маникюр", 
        duration_minutes=90, 
        price=2500, 
        category_id=category.category_id#type: ignore
    )
    
    try:
        category_service.delete_category(category.category_id)#type: ignore
        assert False, "Должна была быть ошибка"
    except ServiceError as e:
        assert "Нельзя удалить категорию" in str(e)
        print("test_delete_category_with_services passed")

def run_all_tests():
    test_service_creation()
    test_service_good_format_time()
    test_delete_service_function()
    test_delete_service_not_found()
    test_service_by_id_function()
    print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")

if __name__ == "__main__":
    run_all_tests()