from typing import List, Optional, Tuple
from models.clients import Client, DiscountLevel

#Класс для вывода информации о клиентах
class ClientUI:
    @staticmethod
    def show_client_details(client: Optional[Client]) -> None:
        """
        Показывает детальную информацию о клиенте
        
        Args:
            client: Объект клиента или None если не найден
        """
        if not client:
            print("Клиент не найден")
            print()
            return
        
        print("ИНФОРМАЦИЯ О КЛИЕНТЕ")
        print()
        print(f"ID: {client.client_id}")
        print(f"Имя: {client.full_name}")
        print(f"Телефон: {client.phone}")
        print(f"Email: {client.email if client.email else 'Не указан'}") #type: ignore
        
        if client.salon_card:
            print(f"Тип скидочной карты: {client.salon_card.discount_level.value}")
            print(f"Суммарные траты: {client.salon_card.total_spent:.2f} руб.")
            print(f"Дата выдачи карты: {client.salon_card.issue_date.strftime('%d.%m.%Y')}")
        print()
    
    @staticmethod
    def show_clients_list(clients: List[Client]) -> None:
        """
        Показывает список клиентов
        
        Args:
            clients: Список клиентов для отображения
        """
        if not clients:
            print("Клиенты не найдены")
            print()
            return
        
        print("СПИСОК КЛИЕНТОВ")
        print()
        for client in clients:
            card_info = ""
            if client.salon_card:
                card_info = f" ({client.salon_card.discount_level.value})"
            print(f"{client.client_id}) {client.full_name}{card_info}")
        print()
    
    @staticmethod
    def show_client_created(client: Client) -> None:
        """
        Сообщение о создании клиента
        
        Args:
            client: Созданный клиент
        """
        print(f"Клиент создан: {client.full_name} (ID: {client.client_id})")
        if client.salon_card:
            print(f"Карта лояльности выдана: {client.salon_card.discount_level.value}")
        print()
    
    @staticmethod
    def show_client_updated(client: Client) -> None:
        """
        Сообщение об успешном обновлении клиента
        
        Args:
            client: Обновленный клиент
        """
        print(f"Данные клиента обновлены: {client.full_name}")
        print()
    
    @staticmethod
    def show_client_deleted(client_id: int, success: bool) -> None:
        """
        Сообщение о результате удаления клиента
        
        Args:
            client_id: ID клиента
            success: True если удален, False если не найден
        """
        if success:
            print(f"Клиент с ID {client_id} удален")
            print()
        else:
            print(f"Клиент с ID {client_id} не найден")
            print()
    
    @staticmethod
    def show_password_changed(success: bool, is_admin: bool = False) -> None:
        """
        Сообщение о результате смены пароля
        
        Args:
            success: True если пароль изменен успешно
            is_admin: True если пароль менял администратор
        """
        if success:
            if is_admin:
                print("Пароль клиента успешно изменен администратором")
            else:
                print("Пароль успешно изменен")
        else:
            print("Не удалось изменить пароль")
        print()

class PurchaseUI:
    """Класс для вывода информации о покупках"""
    
    @staticmethod
    def show_purchase_result(client: Client, discounted_amount: float, 
                            old_level: DiscountLevel, new_level: DiscountLevel) -> None:
        """
        Показывает результат покупки
        
        Args:
            client: Клиент
            discounted_amount: Сумма с учетом скидки
            old_level: Старый уровень карты
            new_level: Новый уровень карты
        """
        print("РЕЗУЛЬТАТ ПОКУПКИ")
        print()
        print(f"Клиент: {client.full_name}")
        print(f"Сумма с учетом скидки: {discounted_amount:.2f} руб.")
        print(f"Всего потрачено: {client.salon_card.total_spent:.2f} руб.")
        print(f"Текущий уровень карты: {new_level.value}")
        
        if old_level != new_level:
            print(f"🎉 Поздравляем! Уровень повышен с {old_level.value} до {new_level.value}!")
        print()
    
    @staticmethod
    def show_purchase_error(error_message: str) -> None:
        """
        Показывает сообщение об ошибке при покупке
        
        Args:
            error_message: Сообщение об ошибке
        """
        print(f"Ошибка при добавлении покупки: {error_message}")
        print()

class AuthUI:
    """Класс для вывода информации аутентификации"""
    
    @staticmethod
    def show_login_prompt() -> Tuple[str, str]:
        """
        Запрашивает данные для входа
        
        Returns:
            Tuple[str, str]: (телефон/email, пароль)
        """
        print("ВХОД В СИСТЕМУ")
        print()
        login = input("Телефон или email: ").strip()
        password = input("Пароль: ").strip()
        return login, password
    
    @staticmethod
    def show_login_success(client: Client) -> None:
        """
        Показывает сообщение об успешном входе
        
        Args:
            client: Авторизованный клиент
        """
        print(f"Добро пожаловать, {client.first_name}!")
        print()
    
    @staticmethod
    def show_login_failed() -> None:
        """Показывает сообщение о неудачном входе"""
        print("Неверный телефон/email или пароль")
        print()