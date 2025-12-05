from sqlalchemy.orm import Session
from typing import List, Optional
from models.masters import Master
from exceptions import MasterError
from auth.authentification import normalize_phone

# для управления мастерами в бд
class MasterService:    
    def __init__(self, session: Session):
        self.session = session

    def add_categories_to_master(self, master_id: int, category_ids: List[int]) -> None:
        """
        Добавляет категории услуг мастеру
        
        Args:
            master_id: ID мастера
            category_ids: Список ID категорий
        """
        from models.services import ServiceCategory
        
        master = self.session.query(Master).filter_by(master_id=master_id).first()
        if not master:
            raise ValueError(f"Мастер с ID {master_id} не найден")
        
        categories = self.session.query(ServiceCategory).filter(ServiceCategory.category_id.in_(category_ids)).all()
        
        if len(categories) != len(category_ids):
            found_ids = [c.category_id for c in categories]
            missing = [c_id for c_id in category_ids if c_id not in found_ids]
            raise ValueError(f"Категории с ID {missing} не найдены")
        

        for category in categories:
            if category not in master.service_categories:
                master.service_categories.append(category)

    def create_master(self, first_name: str, last_name: str, phone: str, email: str, specialty: str, category_ids: Optional[List[int]] = None) -> Master:
        """
        Создает нового мастера в базе данных
        
        Args:
            first_name: Имя мастера
            last_name: Фамилия мастера
            phone: Телефон
            email: Email
            specialty: Специальность
            
        Returns:
            Master: Созданный объект мастера
        """

        existing_phone = self.session.query(Master).filter(Master.phone == normalize_phone(phone)).first()
        if existing_phone:
            raise MasterError(f"Мастер с телефоном {normalize_phone(phone)} уже существует")
    

        if email:
            existing_email = self.session.query(Master).filter(Master.email == email.lower().strip()).first()
            if existing_email:
                raise MasterError(f"Мастер с email {email.lower().strip()} уже существует")

        new_master = Master(first_name=first_name, last_name=last_name, phone=normalize_phone(phone),email=email.lower().strip(), specialty=specialty)
        self.session.add(new_master)
        self.session.flush()
        
        if category_ids:
            self.add_categories_to_master(new_master.master_id, category_ids) #type: ignore
            
        self.session.commit()
        return new_master
    
    def get_master_by_id(self, master_id: int) -> Optional[Master]:
        """
        Находит мастера по ID
        
        Args:
            master_id: ID мастера
            
        Returns:
            Optional[Master]: Найденный мастер или None
        """
        return self.session.query(Master).filter(Master.master_id == master_id).first()
    
    def get_all_masters(self) -> List[Master]:
        """
        Возвращает всех мастеров
        
        Returns:
            List[Master]: Список всех мастеров
        """
        return self.session.query(Master).all()
    
    def get_masters_by_specialty(self, specialty: str) -> List[Master]:
        """
        Находит мастеров по специальности
        
        Args:
            specialty: Специальность для поиска
            
        Returns:
            List[Master]: Список мастеров с указанной специальностью
        """
        return self.session.query(Master).filter(Master.specialty == specialty).all()
    
    def update_master(self, master_id: int, field: str, value: str) -> Master:
        """
        Обновляет поле мастера
        
        Args:
            master_id: ID мастера
            field: Поле для обновления
            value: Новое значение
            
        Returns:
            Master: Обновленный мастер
            
        Raises:
            MasterNotFoundError: Если мастер не найден
            ValueError: Если поле не существует
        """
        master = self.get_master_by_id(master_id)
        if not master:
            raise MasterError(f"Мастер с ID {master_id} не найден")
        
        if not hasattr(master, field.lower().strip()):
            raise ValueError(f"Поле {field} не существует у мастеров")
        
        try:
            setattr(master, field.lower().strip(), value)
            self.session.commit()
            return master
        except Exception as e:
            self.session.rollback()
            raise MasterError(f"Ошибка при обновлении мастера: {e}")
    
    def delete_master(self, master_id: int) -> bool:
        """
        Удаляет мастера по ID
        
        Args:
            master_id: ID мастера для удаления
            
        Returns:
            bool: True если мастер удален, False если не найден
        """
        master = self.get_master_by_id(master_id)
        if master:
            try:
                self.session.delete(master)
                self.session.commit()
                return True
            except Exception as e:
                self.session.rollback()
                raise MasterError(f"Ошибка при удалении мастера: {e}")
        return False

#для управления специальностями 
class SpecialtyService:
    def __init__(self, session: Session):
        self.session = session
    
    def get_all_specialties(self) -> List[str]:
        """Возвращает список всех существующих специальностей

        Returns:
            List[str]: Отсортированный список уникальных специальностей
        """
        specialties = self.session.query(Master.specialty).distinct().all()
        return sorted([spec[0] for spec in specialties if spec[0] is not None])
    
    def get_masters_by_specialty(self, specialty: str) -> List[Master]:
        """
        Находит всех мастеров с указанной специальностью.
    
        Args:
            specialty: Специальность для поиска мастеров
        
        Returns:
            List[Master]: Список мастеров с указанной специальностью. Пустой список, если мастеров не найдено.
        """
        return self.session.query(Master).filter(Master.specialty == specialty).all()