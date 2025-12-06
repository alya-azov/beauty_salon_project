from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from models.clients import Client, SalonCard, DiscountLevel
from auth.authentification import normalize_phone, simple_hash
from exceptions import ClientError

# для управления клиентами в бд
class ClientService:
    def __init__(self, session: Session):
        self.session = session

    def create_client(self, first_name: str, last_name: str, phone: str, 
                     email: str, password: str) -> Client:
        """
        Создает нового клиента
        
        Args:
            first_name: Имя клиента
            last_name: Фамилия клиента
            phone: Номер телефона
            email: Email адрес
            password: Пароль
            
        Returns:
            Client: Созданный клиент
            
        Raises:
            ClientError: Если клиент с таким телефоном или email уже существует
        """
        normalized_phone = normalize_phone(phone)
        normalized_email = email.lower().strip() if email else None
        
        # Проверка уникальности телефона
        existing_phone = self.session.query(Client).filter_by(phone=normalized_phone).first()
        if existing_phone:
            raise ClientError(f"Клиент с телефоном {phone} уже существует")
        
        # Проверка уникальности email 
        if normalized_email:
            existing_email = self.session.query(Client).filter_by(email=normalized_email).first()
            if existing_email:
                raise ClientError(f"Клиент с email {email} уже существует")
        else:
            normalized_email = None
        
        try:
            # Создаем клиента
            new_client = Client(
                first_name=first_name,
                last_name=last_name,
                phone=normalized_phone,
                email=normalized_email,
                password_hash=simple_hash(password)
            )
            
            self.session.add(new_client)
            self.session.flush()
            
            # Создаем карту лояльности
            salon_card = SalonCard(
                client_id=new_client.client_id,
                discount_level=DiscountLevel.STANDARD,
                total_spent=0.0
            )
            
            self.session.add(salon_card)
            self.session.commit()
            
            return new_client
            
        except Exception as e:
            self.session.rollback()
            raise ClientError(f"Ошибка при создании клиента: {e}")    
        
    def get_client_by_id(self, client_id: int) -> Optional[Client]:
        """
        Находит клиента по ID
        
        Args:
            client_id: ID клиента
            
        Returns:
            Optional[Client]: Найденный клиент или None
        """
        return self.session.query(Client).filter(Client.client_id == client_id).first()
    
    def get_client_by_phone(self, phone: str) -> Optional[Client]:
        """
        Находит клиента по номеру телефона
        
        Args:
            phone: Номер телефона
            
        Returns:
            Optional[Client]: Найденный клиент или None
        """
        normalized_phone = normalize_phone(phone)
        if not normalized_phone:
            return None
        return self.session.query(Client).filter(Client.phone == normalized_phone).first()

    
    def get_all_clients(self) -> List[Client]:
        """
        Возвращает всех клиентов
        
        Returns:
            List[Client]: Список всех клиентов
        """
        return self.session.query(Client).all()
    
    def update_client(self, client_id: int, field: str, value: str) -> Client:
        """
        Обновляет информацию о клиенте
        
        Args:
            client_id: ID клиента
            field: Поле для обновления
            value: Новое значение
            
        Returns:
            Client: Обновленный клиент
            
        Raises:
            ClientError: Если клиент не найден или ошибка обновления
        """
        client = self.get_client_by_id(client_id)
        if not client:
            raise ClientError(f"Клиент с ID {client_id} не найден")
        
        if field == "password" or field == "password_hash":
            raise ClientError("Для смены пароля используйте метод change_password")
        
        try:
            if field == "phone":
                normalized_phone = normalize_phone(value)
                existing = self.session.query(Client).filter(Client.phone == normalized_phone, Client.client_id != client_id).first()
                if existing:
                    raise ClientError(f"Телефон {value} уже используется другим клиентом")
                setattr(client, field, normalized_phone)
                
            elif field == "email":
                normalized_email = value.lower().strip()
                existing = self.session.query(Client).filter(Client.email == normalized_email, Client.client_id != client_id).first()
                if existing:
                    raise ClientError(f"Email {value} уже используется другим клиентом")
                setattr(client, field, normalized_email)
                
            else:
                setattr(client, field, value)
            
            self.session.commit()
            return client
            
        except ClientError:
            raise
        except Exception as e:
            self.session.rollback()
            raise ClientError(f"Ошибка при обновлении клиента: {e}")
        
    def change_password(self, client_id: int, old_password: str, new_password: str) -> bool:
        """
        Изменяет пароль клиента
        
        Args:
            client_id: ID клиента
            old_password: Старый пароль
            new_password: Новый пароль
            
        Returns:
            bool: True если пароль изменен успешно
        """
        client = self.get_client_by_id(client_id)
        if not client:
            raise ClientError(f"Клиент с ID {client_id} не найден")
        
        if client.password_hash != simple_hash(old_password): #type:ignore
            raise ClientError("Неверный старый пароль")
        
        client.password_hash = simple_hash(new_password)#type:ignore
        self.session.commit()
        return True

        
    def admin_change_password(self, client_id: int, new_password: str) -> bool:
        """
        Администратор изменяет пароль клиента (без проверки старого)
        
        Args:
            client_id: ID клиента
            new_password: Новый пароль
            
        Returns:
            bool: True если пароль изменен успешно
        """
        client = self.get_client_by_id(client_id)
        if not client:
            raise ClientError(f"Клиент с ID {client_id} не найден")
        
        client.password_hash = simple_hash(new_password)#type:ignore
        self.session.commit()
        return True
    
    def delete_client(self, client_id: int) -> bool:
        """
        Удаляет клиента
        
        Args:
            client_id: ID клиента для удаления
            
        Returns:
            bool: True если клиент удален
        """
        client = self.get_client_by_id(client_id)
        if not client:
            return False
        
        self.session.delete(client)
        self.session.commit()
        return True

# для управления покупками (для карты салона) в бд
class PurchaseService:
    def __init__(self, session: Session):
        self.session = session
    
    def add_purchase(self, client_id: int, amount: float) -> Tuple[Client, float, DiscountLevel, DiscountLevel]:
        """
        Добавляет покупку клиенту и обновляет карту лояльности
        
        Args:
            client_id: ID клиента
            amount: Сумма покупки
            
        Returns:
            Tuple[Client, float, DiscountLevel, DiscountLevel]: 
                (клиент, сумма с учетом скидки, старый уровень, новый уровень)
            
        Raises:
            ClientError: Если клиент не найден или сумма некорректна
        """
        if amount <= 0:
            raise ClientError("Сумма покупки должна быть положительной")
        
        client = self.session.query(Client).filter(Client.client_id == client_id).first()
        if not client or not client.salon_card:
            raise ClientError(f"Клиент с ID {client_id} не найден или у него нет карты лояльности")
        
        discounted_amount = client.salon_card.apply_discount(amount)
        old_level = client.salon_card.discount_level
        client.salon_card.total_spent += discounted_amount
        client.salon_card.upgrade_level()
        new_level = client.salon_card.discount_level
        self.session.commit()
            
        return client, discounted_amount, old_level, new_level
