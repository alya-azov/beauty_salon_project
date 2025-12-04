from typing import Tuple
from models.clients import Client, DiscountLevel
from auth.authentification import format_phone
from exceptions import ClientError

class AuthUI:
    """Класс для отображения интерфейса аутентификации"""
    
    @staticmethod
    def show_client_login_prompt() -> Tuple[str, str]:
        """
        Запрашивает данные для входа клиента
        
        Returns:
            Tuple[str, str]: (телефон, пароль)
        """
        print("ВХОД ДЛЯ КЛИЕНТА")
        print()
        phone = input("Телефон: ").strip()
        password = input("Пароль: ").strip()
        return phone, password
    
    @staticmethod
    def show_admin_login_prompt() -> Tuple[str, str]:
        """
        Запрашивает данные для входа администратора
        
        Returns:
            Tuple[str, str]: (логин, пароль)
        """
        print("ВХОД ДЛЯ АДМИНИСТРАТОРА")
        print()
        username = input("Логин: ").strip()
        password = input("Пароль: ").strip()
        return username, password
    
    @staticmethod
    def show_client_registration_prompt() -> Tuple[str, str, str, str, str]:
        """
        Запрашивает данные для регистрации нового клиента
        
        Returns:
            Tuple[str, str, str, str, str]: 
                (имя, фамилия, телефон, email, пароль)
        """
        print("РЕГИСТРАЦИЯ НОВОГО КЛИЕНТА")
        print()
        first_name = input("Имя: ").strip()
        last_name = input("Фамилия: ").strip()
        
        phone = input("Телефон: ").strip()
        email = input("Email (необязательно): ").strip()
        
        password = input("Пароль: ").strip()
        confirm_password = input("Подтвердите пароль: ").strip()
        
        if password != confirm_password:
            raise ClientError("Пароли не совпадают")
        
        if len(password) < 6:
            raise ClientError("Пароль должен содержать минимум 6 символов")
            
        return first_name, last_name, phone, email, password
    
    @staticmethod
    def show_client_login_success(client: Client) -> None:
        """
        Показывает сообщение об успешном входе клиента
        
        Args:
            client: Авторизованный клиент
        """
        print("ВХОД ВЫПОЛНЕН УСПЕШНО!")
        print(f"Добро пожаловать, {client.first_name} {client.last_name}!")
        
        if client.salon_card:
            card = client.salon_card
            print(f"Ваш уровень карты: {card.discount_level.value}")
            print(f"Накопленная сумма: {card.total_spent:.2f} руб.")
            if card.discount_level != DiscountLevel.STANDARD:
                discount_rate = {
                    DiscountLevel.SILVER: "3%",
                    DiscountLevel.GOLD: "7%", 
                    DiscountLevel.PLATINUM: "10%"
                }[card.discount_level]
                print(f"Ваша скидка: {discount_rate}")
        
        print()
    
    @staticmethod
    def show_admin_login_success() -> None:
        """
        Показывает сообщение об успешном входе администратора
        """
        print("ВХОД АДМИНИСТРАТОРА УСПЕШЕН!")
        print("Добро пожаловать в панель управления!")
        print()
    
    @staticmethod
    def show_client_login_failed(reason: str = "Неверный телефон или пароль") -> None:
        """
        Показывает сообщение о неудачном входе клиента
        
        Args:
            reason: Причина ошибки
        """
        print("ОШИБКА ВХОДА")
        print(f"Причина: {reason}")
        print()
    
    @staticmethod
    def show_admin_login_failed() -> None:
        """
        Показывает сообщение о неудачном входе администратора
        """
        print("ОШИБКА ВХОДА АДМИНИСТРАТОРА")
        print("Неверный логин или пароль")
        print()
    
    @staticmethod
    def show_registration_success(client: Client) -> None:
        """
        Показывает сообщение об успешной регистрации
        
        Args:
            client: Зарегистрированный клиент
        """
        print("РЕГИСТРАЦИЯ УСПЕШНА!")
        print(f"Клиент создан: {client.full_name}")
        print(f"ID: {client.client_id}")
        print(f"Телефон: {format_phone(client.phone)}") #type: ignore
        if client.email:#type: ignore
            print(f"Email: {client.email}")
        print("Карта лояльности активирована со стандартным уровнем")
        print()
    
    @staticmethod
    def show_registration_error(error: str) -> None:
        """
        Показывает сообщение об ошибке регистрации
        
        Args:
            error: Текст ошибки
        """
        print("ОШИБКА РЕГИСТРАЦИИ")
        print(f"Причина: {error}")
        print()
    
    @staticmethod
    def show_password_change_prompt() -> Tuple[str, str, str]:
        """
        Запрашивает данные для смены пароля
        
        Returns:
            Tuple[str, str, str]: (старый пароль, новый пароль, подтверждение)
        """
        print("СМЕНА ПАРОЛЯ")
        print()
        old_password = input("Старый пароль: ").strip()
        new_password = input("Новый пароль: ").strip()
        confirm_password = input("Подтвердите новый пароль: ").strip()
        return old_password, new_password, confirm_password
    
    @staticmethod
    def show_admin_password_change_prompt() -> Tuple[str, str]:
        """
        Запрашивает данные для смены пароля администратором
        
        Returns:
            Tuple[str, str]: (новый пароль, подтверждение)
        """
        print("СМЕНА ПАРОЛЯ КЛИЕНТА (АДМИНИСТРАТОР)")
        print()
        new_password = input("Новый пароль: ").strip()
        confirm_password = input("Подтвердите новый пароль: ").strip()
        return new_password, confirm_password
    
    @staticmethod
    def show_password_change_success(is_admin: bool) -> None:
        """
        Показывает сообщение об успешной смене пароля
        
        Args:
            is_admin: True если пароль менял администратор
        """
        if is_admin:
            print("ПАРОЛЬ КЛИЕНТА УСПЕШНО ИЗМЕНЕН АДМИНИСТРАТОРОМ")
        else:
            print("ПАРОЛЬ УСПЕШНО ИЗМЕНЕН")
        print()
    
    @staticmethod
    def show_password_change_error(reason: str) -> None:
        """
        Показывает сообщение об ошибке смены пароля
        
        Args:
            reason: Причина ошибки
        """
        print("ОШИБКА СМЕНЫ ПАРОЛЯ")
        print(f"Причина: {reason}")
        print()