from models.services import Service, ServiceCategory
from sqlalchemy.orm import Session
from typing import Optional

# добавить новую услугу
def add_service(session: Session, service_name: str, duration_minutes: int, 
                price: int, category_id: int) -> Optional[Service]:
    # Если категории нет в списке - спрашиваем подтверждение
    category = session.query(ServiceCategory).filter_by(category_id=category_id).first()
    if not category:
        print("Добавление услуги отменено, нет такой категории")
        return None
    
    new_service = Service(service_name=service_name, duration_minutes=duration_minutes,
                          price=price, category_id=category_id)

    session.add(new_service)
    session.commit()
    print(f"Новая услуга добавлена: {service_name}")
    print()
    return new_service

# удалить услугу
def delete_service(session: Session, service_id: int) -> bool:
    service = session.query(Service).filter(Service.service_id == service_id).first()
    if service:
        session.delete(service)
        session.commit()
        print("Услуга удалена!")
        print()
        return True
    return False

# обновить данные по услуге
def update_service(session: Session, service_id: int, field: str, value: str) -> bool:
    service = session.query(Service).filter(Service.service_id == service_id).first()
    if service:
        if field == 'category_id':
            category = session.query(ServiceCategory).filter_by(category_id=value).first()
            if not category:
                print("Категории с ID " + str(value) + " не существует!")
                return False

        setattr(service, field, value)
        session.commit()
        print("Данные обновлены!")
        print()
        return True
    return False

# вывести услугу по id
def service_by_id(session: Session, service_id: int) -> Optional[Service]:
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
def get_all_services(session: Session) -> None:
    services = session.query(Service).all()
    for service in services:
        print(str(service.service_id) + ") " + service.service_name + " - " + 
              str(service.price) + " руб., " + service.good_format_time)
    print()

# вывести услуги по категории
def get_services_by_category(session: Session, category_id: int) -> None:
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
def get_all_categories(session: Session) -> None:
    categories = session.query(ServiceCategory).all()
    for category in categories:
        print(str(category.category_id) + ") " + category.category_name)
    print()

# добавить новый тип категории
def add_new_category(session: Session, category_name: str) -> bool:
    new_c = session.query(ServiceCategory).filter_by(category_name=category_name).first()
    if new_c:
        print("Категория '" + category_name + "' уже существует")
        return False
    
    new_category = ServiceCategory(category_name=category_name)
    session.add(new_category)
    session.commit()
    print("Новая категория '" + category_name + "' добавлена!")
    return True

# удалить категорию
def delete_category(session: Session, category_id: int) -> bool:
    category = session.query(ServiceCategory).filter_by(category_id=category_id).first()
    if not category:
        print("Категория с ID " + str(category_id) + " не найдена")
        return False
    
    # проверяем есть ли услуги в этой категории
    services_in_category = session.query(Service).filter_by(category_id=category_id).count()
    if services_in_category > 0:
        print("Нельзя удалить категорию! В ней есть услуги")
        return False
    
    session.delete(category)
    session.commit()
    print("Категория '" + category.category_name + "' удалена!")
    return True

