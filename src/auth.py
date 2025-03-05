import requests
from interfaces import IAuth
import logging

logger = logging.getLogger(__name__)


class Auth(IAuth):
    def __init__(self, session: requests.Session, base_url: str, headers: dict):
        self.session = session
        self.base_url = base_url
        self.headers = headers

    def login(self, username: str, password: str) -> bool:
        login_data = {
            "return_url": "index.php",
            "redirect_url": "index.php",
            "user_login": username,
            "password": password,
            "dispatch[auth.login]": "",
        }
        response = self.session.post(
            self.base_url, data=login_data, headers=self.headers
        )
        if response.status_code == 200:
            if "cp_email" in self.session.cookies:
                logger.info("Успешная авторизация")
                return True
            else:
                logger.error("Ошибка авторизации: неверный логин или пароль")
                return False
        else:
            logger.error(f"Ошибка авторизации. Код статуса: {response.status_code}")
            return False
