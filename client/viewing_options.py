from models.masters import Master
from sqlalchemy.orm import Session
from models.services import Service, ServiceCategory
from typing import Optional

# вывести всех мастеров (нет не из себя)
def show_all_masters(session: Session) -> None:
    masters = session.query(Master).all()
    for master in masters:
        print(str(master.master_id) + ") " + master.first_name + " " + master.last_name + " " + master.specialty)
    print()


# вывести мастеров по специальности
def show_masters_by_specialty(session: Session, specialty: str) -> None:
    masters = session.query(Master).filter(Master.specialty == specialty).all()
    print("Мастера специальности: " + specialty)
    for master in masters:
        print(str(master.master_id) + ") " + master.first_name + " " + master.last_name)
    print()

# вывести мастера по id
def show_master_by_id(session: Session, master_id: int) -> Optional[Master]:
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

# вывести услугу по id
def show_service_details(session: Session, service_id: int) -> Optional[Service]:
    service = session.query(Service).filter(Service.service_id == service_id).first()
    if service:
        print("id: " + str(service.service_id))
        print("Название: " + service.service_name)
        print("Длительность: " + service.good_format_time)
        print("Цена: " + str(service.price) + " руб.")
        category = session.query(ServiceCategory).filter_by(category_id=service.category_id).first()
        if category:
            print("Категория: " + category.category_name)
        else:
            print("Категория: не найдена")
        return service
    else:
        print("Услуга не найдена")
        return None
    print()

# вывести все услуги
def show_all_services(session: Session) -> None:
    services = session.query(Service).all()
    for service in services:
        print(str(service.service_id) + ") " + service.service_name + " - " + 
              str(service.price) + " руб., " + service.good_format_time)
    print()

# вывести услуги по категории
def show_services_by_category(session: Session, category_id: int) -> None:
    services = session.query(Service).filter(Service.category_id == category_id).all()
    category = session.query(ServiceCategory).filter_by(category_id=category_id).first()

    if category:
        print("Услуги категории: " + category.category_name)
        for service in services:
            print(str(service.service_id) + ") " + service.service_name + " - " + str(service.price) + " руб.")
        print()
    else:
        print("Категория не найдена") 

# вывести все возможные категории
def show_all_categories(session: Session):
    categories = session.query(ServiceCategory).all()
    for category in categories:
        print(str(category.category_id) + ") " + category.category_name)
    print()
