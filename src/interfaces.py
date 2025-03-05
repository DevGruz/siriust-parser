from abc import ABC, abstractmethod
from typing import Any


class IAuth(ABC):
    @abstractmethod
    def login(self, username: str, password: str) -> bool:
        pass


class IDataParser(ABC):
    @abstractmethod
    def get_personal_info(self) -> dict:
        pass

    @abstractmethod
    def get_wishlist_products(self) -> list:
        pass

    @abstractmethod
    def get_product_details(self, product_url: str) -> dict:
        pass


class IStorage(ABC):
    @abstractmethod
    def save_personal_info(self, personal_info: dict[str, str]) -> None:
        pass

    @abstractmethod
    def save_wishlist_products(self, product_urls: list[str]) -> None:
        pass

    @abstractmethod
    def save_product_details(self, product_details: dict[str, Any]) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
