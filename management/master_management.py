from sqlalchemy.orm import Session
from typing import List, Optional
from models.masters import Master
from exceptions import MasterError
from auth.authentification import normalize_phone

# для управления мастерами в бд
class MasterService:    
    def __init__(self, session: Session):
        self.session = session
    
    def create_master(self, first_name: str, last_name: str, phone: str, 
                     email: str, specialty: str) -> Master:
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
            
        Raises:
            MasterError: Если не удалось создать мастера
        """
        try:
            new_master = Master(first_name=first_name, last_name=last_name, phone=normalize_phone(phone),email=email.lower().strip(), specialty=specialty)
            
            self.session.add(new_master)
            self.session.commit()
            return new_master
            
        except Exception as e:
            self.session.rollback()
            raise MasterError(f"Ошибка при создании мастера: {e}")
    
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
            raise ValueError(f"Поле {field} не существует в модели Master")
        
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

#ля работы со специальностями мастеров
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