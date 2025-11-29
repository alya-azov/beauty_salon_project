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