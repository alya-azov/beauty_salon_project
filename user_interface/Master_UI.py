from models.masters import Master
from sqlalchemy.orm import Session
from models.services import Service, ServiceCategory
from auth.authentification import format_phone
from typing import List, Optional
from models.masters import Master

#Класс для вывода информации о мастерах
class MasterUI:
    @staticmethod
    def show_master_details(master: Optional[Master]) -> None:
        """
        Показывает детальную информацию о мастере.
        
        Args:
            master: Объект мастера или None если не найден
        """
        if not master:
            print("Мастер не найден")
            return
        
        print("ИНФОРМАЦИЯ О МАСТЕРЕ")
        print()
        print(f"ID: {master.master_id}")
        print(f"Имя: {master.full_name}")
        print(f"Телефон: {format_phone(str(master.phone))}")
        print(f"Email: {master.email}")
        print(f"Специальность: {master.specialty}")
        print(f"Полное имя: {master.full_name}")
        print()
    
    @staticmethod
    def show_masters_list(masters: List[Master]) -> None:
        """
        Показывает список мастеров в сокращенном формате.
        
        Args:
            masters: Список мастеров для отображения
        """
        print("\n" + "=" * 40)
        print("ВСЕ МАСТЕРЫ")
        print("=" * 40)
        for master in masters:
            print(f"  {master.master_id}) {master.full_name} - {master.specialty}")
            print()
        print("=" * 40)
    
    @staticmethod
    def show_master_created(master: Master) -> None:
        """
        Сообщение об успешном создании мастера.
        
        Args:
            master: Созданный мастер
        """
        print(f"Мастер создан: {master.full_name} (ID: {master.master_id})")
        print()
    
    @staticmethod
    def show_master_updated(master: Master) -> None:
        """
        Сообщение об успешном обновлении мастера.
        
        Args:
            master: Обновленный мастер
        """
        print(f"Данные мастера обновлены: {master.full_name}")
        print()
    
    @staticmethod
    def show_master_deleted(master_id: int, success: bool) -> None:
        """
        Сообщение о результате удаления мастера.
        
        Args:
            master_id: ID мастера
            success: True если удален, False если не найден
        """
        if success:
            print(f"Мастер с ID {master_id} удален")
            print()
        else:
            print(f"Мастер не найден")
            print()

#Класс для вывода информации о специальностях
class SpecialtyUI:    
    @staticmethod
    def show_all_specialties(specialties: List[str]) -> None:
        """
        Показывает все существующие специальности.
        
        Args:
            specialties: Список специальностей
        """
        if not specialties:
            print("Специальности не найдены")
            print()
            return
        
        for i, specialty in enumerate(specialties, 1):
            print(str(i) + ")" + specialty)
        print()
    
    @staticmethod
    def show_masters_by_specialty(specialty: str, masters: List[Master]) -> None:
        """
        Показывает мастеров по специальности.
        
        Args:
            specialty: Название специальности
            masters: Список мастеров с этой специальностью
        """
        if not masters:
            print("Мастеров не найдено")
            return
        
        print(f"Мастера специальности '{specialty}':")
        for master in masters:
            print(f"  {master.master_id}) {master.full_name} - {master.phone}")
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
            print()
        else:
            print("Категория: не найдена")
            print()
        return service
    else:
        print("Услуга не найдена")
        return None
    print()

