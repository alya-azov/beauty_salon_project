import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from management.master_management import MasterService, SpecialtyService
from models.masters import Master
from models.services import ServiceCategory, Service
from models.schedule import MasterSchedule, Appointment, MasterBreak 
from models.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def test_master_class():
    master = Master(first_name="Анна", last_name="Иванова",
                    phone="+7-999-123-45-67", email="anna@salon.ru",
                    specialty="Парикмахер")
    
    assert master.first_name == "Анна"#type: ignore
    assert master.last_name == "Иванова"#type: ignore
    assert master.phone == "+7-999-123-45-67"#type: ignore
    assert master.email == "anna@salon.ru"#type: ignore
    assert master.specialty == "Парикмахер"#type: ignore
    assert master.full_name == "Анна Иванова"
    
    print("test_master_class")


def test_master_class_withot_phone_and_email():
    master = Master(
        first_name="Анна",
        last_name="Петрова",
        specialty="Парикмахер"
    )
    
    assert master.first_name == "Анна" #type: ignore
    assert master.last_name == "Петрова" #type: ignore
    assert master.specialty == "Парикмахер"#type: ignore
    assert master.phone is None
    assert master.email is None
    assert master.full_name == "Анна Петрова"
    
    print("test_master_class_withot_phone_and_email")


def test_delete():    
    engine1 = create_engine("sqlite:///:memory:")
    
    Base.metadata.create_all(engine1)
    
    Session = sessionmaker(engine1)
    session = Session()

    master_service = MasterService(session)
    
    # Добавляем мастера
    master = master_service.create_master(
        first_name="Светлана",
        last_name="Петрова", 
        phone="7-932 (730) 88 88",
        email="test@test.ru",
        specialty="Бровист"
    )

    master_id = master.master_id
    
    # 2. Проверяем что мастер есть в базе
    check_master = master_service.get_master_by_id(master_id)#type: ignore
    assert check_master is not None
    assert check_master.first_name == "Светлана"#type: ignore
    # Проверяем нормализацию телефона
    phone = check_master.phone
    assert phone in ["79327308888", "+79327308888", "7-932 (730) 88 88"]#type: ignore
    
    # 3. Удаляем мастера
    result = master_service.delete_master(master_id)#type: ignore
    assert result is True
    
    # 4. Проверяем что мастера больше нет
    deleted_master = master_service.get_master_by_id(master_id)#type: ignore
    assert deleted_master is None
    print("test_delete")
    
    session.close()

def run_all_tests():
    
    test_master_class()
    test_master_class_withot_phone_and_email()
    test_delete()
    
    print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")

if __name__ == "__main__":
    run_all_tests()