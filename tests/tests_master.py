import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from admin.master_management import add_master, delete_master
from models.masters import Master, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def test_master_class():
    # Создаем мастера
    master = Master(first_name="Анна", last_name="Иванова",
                    phone="+7-999-123-45-67", email="anna@salon.ru",
                    specialty="Парикмахер")
    
    assert master.first_name == "Анна"
    assert master.last_name == "Иванова"
    assert master.phone == "+7-999-123-45-67"
    assert master.email == "anna@salon.ru"
    assert master.specialty == "Парикмахер"
    assert master.full_name == "Анна Иванова"
    
    print("test_master_class")


def test_master_class_withot_phone_and_email():
    # Создаем мастера без телефона и email
    master = Master(
        first_name="Анна",
        last_name="Петрова",
        specialty="Парикмахер"
    )
    
    assert master.first_name == "Анна"
    assert master.last_name == "Петрова"
    assert master.specialty == "Парикмахер"
    assert master.phone is None
    assert master.email is None
    assert master.full_name == "Анна Петрова"
    
    print("test_master_class_withot_phone_and_email")


def test_delete():    
    engine1 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine1)
    Session = sessionmaker(engine1)
    session = Session()
    
    # Добавляем мастера
    master = add_master(
        session=session,
        first_name="Светлана",
        last_name="Петрова", 
        phone="111",
        email="@test.ru",
        specialty="Бровист"
    )

    master_id = master.master_id
    
    # 2. Проверяем что мастер есть в базе
    check_master = session.query(Master).filter_by(master_id=master_id).first()
    assert check_master is not None
    assert check_master.first_name == "Светлана"
    
    # 3. Удаляем мастера
    result = delete_master(session, master_id)
    assert result is True
    
    # 4. Проверяем что мастера больше нет
    deleted_master = session.query(Master).filter_by(master_id=master_id).first()
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