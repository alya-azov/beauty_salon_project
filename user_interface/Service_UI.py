from typing import List, Optional
from models.services import Service, ServiceCategory

#Класс для вывода информации об услугах
class ServiceUI:
    @staticmethod
    def show_service_details(service: Optional[Service]) -> None:
        """
        Показывает детальную информацию об услуге
        
        Args:
            service: Объект услуги или None если не найдена
        """
        if not service:
            print("Услуга не найдена")
            print()
            return
        
        print("ИНФОРМАЦИЯ ОБ УСЛУГЕ")
        print()
        print(f"ID: {service.service_id}")
        print(f"Название: {service.service_name}")
        print(f"Длительность: {service.good_format_time}")
        print(f"Цена: {service.price} руб.")
        if service.category:
            print(f"Категория: {service.category.category_name}")
        print()
    
    @staticmethod
    def show_services_list(services: List[Service]) -> None:
        """
        Показывает список услуг
        
        Args:
            services: Список услуг для отображения
        """
        if not services:
            print("Услуги не найдены")
            print()
            return
        
        for service in services:
            category_name = service.category.category_name if service.category else "Без категории"
            print(f"  {service.service_id}) {service.service_name} - {service.price} руб., {service.good_format_time} ({category_name})")
            print()
    
    @staticmethod
    def show_services_by_category(category: ServiceCategory, services: List[Service]) -> None:
        """
        Показывает услуги по категории
        
        Args:
            category: Категория услуг
            services: Список услуг в этой категории
        """
        if not services:
            print("  Услуг не найдено")
            print()
            return
        
        for service in services:
            print(f"  {service.service_id}) {service.service_name} - {service.price} руб., {service.good_format_time}")
            print()
    
    @staticmethod
    def show_service_created(service: Service) -> None:
        """
        Сообщение о создании услуги
        
        Args:
            service: Созданная услуга
        """
        print(f"Услуга создана: {service.service_name} (ID: {service.service_id})")
        print()
    
    @staticmethod
    def show_service_updated(service: Service) -> None:
        """
        Сообщение об успешном обновлении услуги
        
        Args:
            service: Обновленная услуга
        """
        print(f"Данные услуги обновлены: {service.service_name}")
        print()
    
    @staticmethod
    def show_service_deleted(service_id: int, success: bool) -> None:
        """
        Сообщение о результате удаления услуги
        
        Args:
            service_id: ID услуги
            success: True если удалена, False если не найдена
        """
        if success:
            print(f"Услуга с ID {service_id} удалена")
            print()
        else:
            print(f"Услуга не найдена")
            print()

#Класс для вывода информации о категориях
class CategoryUI:
    """Класс для вывода информации о категориях"""
    
    @staticmethod
    def show_all_categories(categories: List[ServiceCategory]) -> None:
        """
        Показывает список категорий
        
        Args:
            categories: Список категорий для отображения
        """
        if not categories:
            print("Категории не найдены")
            print()
            return
    
        for category in categories:
            print(f"  {category.category_id}) {category.category_name}")
    
    @staticmethod
    def show_category_created(category: ServiceCategory) -> None:
        """
        Сообщение об успешном создании категории
        
        Args:
            category: Созданная категория
        """
        print(f"Категория создана: {category.category_name} (ID: {category.category_id})")
        print()
    
    @staticmethod
    def show_category_deleted(category_id: int, success: bool) -> None:
        """
        Сообщение о результате удаления категории
        
        Args:
            category_id: ID категории
            success: True если удалена, False если не найдена
        """
        if success:
            print(f"Категория с ID {category_id} удалена")
            print()
        else:
            print(f"Категория с ID {category_id} не найдена")
            print()