# временное решение, чтобы пока не прописывать логику захода в аккаунт

def authenticate_user(login: str, password: str) -> str:
    """
    Аутентифицирует пользователя по логину и паролю.
    """
    if login == "admin" and password == "admin123":
        return "admin"
    elif login == "client" and password == "client123":
        return "client"
    else:
        return "invalid"