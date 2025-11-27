from models.masters import Master
from sqlalchemy.orm import Session
from typing import Optional


# добавить нового мастера
def add_master(session: Session, first_name: str, last_name: str, phone: str, email: str, specialty: str) -> Master:
    """
    добавляет нового мастера в бд
    """
    new_m = Master(
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        email=email,
        specialty=specialty,
    )

    session.add(new_m)
    session.commit()
    print("Новый мастер добавлен: " + new_m.first_name + " " + new_m.last_name)
    print()
    return new_m


# удалить мастера
def delete_master(session: Session, master_id: int) -> bool:
    master = session.query(Master).filter(Master.master_id == master_id).first()
    if master:
        session.delete(master)
        session.commit()
        print("Мастер удален!")
        print()
        return True
    return False


# обновить данные по мастеру
def update_master(session: Session, master_id: int, field: str, value: str) -> bool:
    master = session.query(Master).filter(Master.master_id == master_id).first()
    if master:
        setattr(master, field, value)
        session.commit()
        print("Данные обновлены!")
        print()
        return True
    return False


# вывести мастера по id
def master_by_id(session: Session, master_id: int) -> Optional[Master]:
    master = session.query(Master).filter(Master.master_id == master_id).first()
    if master:
        print("id: " + str(master.master_id))
        print("Имя: " + master.first_name)
        print("Фамилия: " + master.last_name)
        print("Телефон: " + master.phone)
        print("Email: " + master.email)
        print("Специальность: " + master.specialty)
        return master
    else:
        print("Мастер не найден")
        return None
    print()


# вывести всех мастеров (нет не из себя)
def get_all_masters(session: Session) -> None:
    masters = session.query(Master).all()
    for master in masters:
        print(str(master.master_id) + ") " + master.first_name + " " + master.last_name + " " + master.specialty)
    print()


# вывести мастеров по специальности
def get_masters_by_specialty(session: Session, specialty: str) -> None:
    masters = session.query(Master).filter(Master.specialty == specialty).all()
    print("Мастера специальности: " + specialty)
    for master in masters:
        print(str(master.master_id) + ") " + master.first_name + " " + master.last_name)
    print()
