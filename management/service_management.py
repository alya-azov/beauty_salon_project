from sqlalchemy.orm import Session
from typing import List, Optional
from models.services import Service, ServiceCategory
from exceptions import ServiceError

# для управления услугами в бд
class ServiceService:
    def __init__(self, session: Session):
        self.session = session
    
    def create_service(self, service_name: str, duration_minutes: int, 
                      price: int, category_id: int) -> Service:
        """
        Создает новую услугу
        
        Args:
            service_name: Название услуги
            duration_minutes: Длительность в минутах
            price: Цена услуги
            category_id: ID категории
            
        Returns:
            Service: Созданная услуга
            
        Raises:
            ServiceError: Если категория не найдена или ошибка создания
        """
        category = self.session.query(ServiceCategory).filter_by(category_id=category_id).first()
        if not category:
            raise ServiceError(f"Категория с ID {category_id} не найдена")
        
        if duration_minutes % 30 != 0:
            raise ServiceError(f"Длительность услуги должна быть кратной 30 минутам.")
        
        try:
            new_service = Service(
                service_name=service_name,
                duration_minutes=duration_minutes,
                price=price,
                category_id=category_id
            )
            
            self.session.add(new_service)
            self.session.commit()
            return new_service
            
        except Exception as e:
            self.session.rollback()
            raise ServiceError(f"Ошибка при создании услуги: {e}")
    
    def get_service_by_id(self, service_id: int) -> Optional[Service]:
        """
        Находит услугу по ID
        
        Args:
            service_id: ID услуги
            
        Returns:
            Optional[Service]: Найденная услуга или None
        """
        return self.session.query(Service).filter(Service.service_id == service_id).first()
    
    def get_all_services(self) -> List[Service]:
        """
        Возвращает все услуги
        
        Returns:
            List[Service]: Список всех услуг
        """
        return self.session.query(Service).all()
    
    def get_services_by_category(self, category_id: int) -> List[Service]:
        """
        Находит услуги по категории
        
        Args:
            category_id: ID категории
            
        Returns:
            List[Service]: Список услуг с указанной категорией
        """
        return self.session.query(Service).filter(Service.category_id == category_id).all()
    
    def update_service(self, service_id: int, field: str, value: str) -> Optional[Service]:
        """
        Обновляет поле услуги
    
        Args:
        service_id: ID услуги
        field: Поле для обновления
        value: Новое значение 
            
        Returns:
        Service: Обновленная услуга
            
        Raises:
        ServiceError: Если услуга не найдена или ошибка обновления
        """
        service = self.get_service_by_id(service_id)
        if not service:
            raise ServiceError(f"Услуга с ID {service_id} не найдена")
    
        if not hasattr(service, field):
            raise ServiceError(f"Поле {field} не существует в модели Service")
    
    
        # Валидация для поля category_id
        if field == 'category_id':
            try:
                category_id_int = int(value)
                category = self.session.query(ServiceCategory).filter_by(category_id=category_id_int).first()
                if not category:
                    raise ServiceError(f"Категории с ID {category_id_int} не существует")
                n_value = category_id_int
            except ValueError:
                raise ServiceError(f"ID категории должно быть числом")
    
        # Валидация для поля duration_minutes
        elif field == 'duration_minutes':
            try:
                duration_int = int(value)
                if duration_int <= 0:
                    raise ServiceError(f"Длительность должна быть положительным числом")
                if duration_int % 30 != 0:
                    raise ServiceError(f"Длительность услуги должна быть кратной 30 минутам")
                n_value = duration_int
            except ValueError:
                raise ServiceError(f"Длительность должна быть числом")
    
        # Валидация для поля price
        elif field == 'price':
            try:
                price_int = int(value)
                if price_int <= 0:
                    raise ServiceError(f"Цена должна быть ")
                n_value = price_int
            except ValueError:
                raise ServiceError(f"Цена должна быть числом")
    
        # Валидация для поля service_name
        elif field == 'service_name':
            if not str(value).strip():
                raise ServiceError(f"Название услуги не может быть пустым")
            n_value = str(value).strip()


        try:
            setattr(service, field, n_value)
            self.session.commit()
            return service
        except Exception as e:
            self.session.rollback()
            raise ServiceError(f"Ошибка при обновлении услуги: {e}")
    
    def delete_service(self, service_id: int) -> bool:
        """
        Удаляет услугу по ID
        
        Args:
            service_id: ID услуги для удаления
            
        Returns:
            bool: True если услуга удалена, False если не найдена
            
        Raises:
            ServiceError: Если ошибка при удалении
        """
        service = self.get_service_by_id(service_id)
        if service:
            try:
                self.session.delete(service)
                self.session.commit()
                return True
            except Exception as e:
                self.session.rollback()
                raise ServiceError(f"Ошибка при удалении услуги: {e}")
        return False

# для управления категориями услуг в бд
class CategoryService:
    def __init__(self, session: Session):
        self.session = session
    
    def create_category(self, category_name: str) -> ServiceCategory:
        """
        Создает новую категорию
        
        Args:
            category_name: Название категории
            
        Returns:
            ServiceCategory: Созданная категория
            
        Raises:
            ServiceError: Если категория уже существует или ошибка создания
        """
        existing_category = self.session.query(ServiceCategory).filter_by(category_name=category_name.lower().strip()).first()
        if existing_category:
            raise ServiceError(f"Категория '{category_name}' уже существует")
        
        try:
            new_category = ServiceCategory(category_name=category_name.lower().strip())
            self.session.add(new_category)
            self.session.commit()
            return new_category
        except Exception as e:
            self.session.rollback()
            raise ServiceError(f"Ошибка при создании категории: {e}")
    
    def get_category_by_id(self, category_id: int) -> Optional[ServiceCategory]:
        """
        Находит категорию по ID
        
        Args:
            category_id: ID категории
            
        Returns:
            Optional[ServiceCategory]: Найденная категория или None
        """
        return self.session.query(ServiceCategory).filter_by(category_id=category_id).first()
    
    def get_all_categories(self) -> List[ServiceCategory]:
        """
        Возвращает все категории
        
        Returns:
            List[ServiceCategory]: Список всех категорий
        """
        return self.session.query(ServiceCategory).all()
    
    def delete_category(self, category_id: int) -> bool:
        """
        Удаляет категорию по ID
        
        Args:
            category_id: ID категории для удаления
            
        Returns:
            bool: True если категория удалена, False если не найдена
            
        Raises:
            ServiceError: Если в категории есть услуги или ошибка удаления
        """
        category = self.get_category_by_id(category_id)
        if not category:
            return False
        
        # Проверяем есть ли услуги в этой категории
        services_count = self.session.query(Service).filter_by(category_id=category_id).count()
        if services_count > 0:
            raise ServiceError(f"Нельзя удалить категорию! В ней есть услуги")
        
        try:
            self.session.delete(category)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ServiceError(f"Ошибка при удалении категории: {e}")