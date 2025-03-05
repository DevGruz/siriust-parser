import json
import logging
import sqlite3
from typing import Any, Dict, List

from interfaces import IStorage

logger = logging.getLogger(__name__)


class SQLiteStorage(IStorage):
    def __init__(self, db_name: str = "siriust_data.db"):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        self._create_tables()
        logger.info(f"Инициализировано SQLite-хранилище: {self.db_name}")

    def _create_tables(self):
        """Создает таблицы в базе данных, если они не существуют."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS personal_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT,
                first_name TEXT,
                last_name TEXT,
                city TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS wishlist_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_url TEXT UNIQUE
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                price_retail TEXT,
                price_wholesale TEXT,
                rating REAL,
                reviews_count INTEGER,
                stores_count INTEGER
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                author TEXT,
                rating REAL,
                date TEXT,
                message TEXT,
                FOREIGN KEY (product_id) REFERENCES product_details (id)
            )
        """)

        self.connection.commit()
        logger.info("Таблицы в SQLite созданы или уже существуют.")

    def save_personal_info(self, personal_info: Dict[str, str]) -> None:
        """Сохраняет персональные данные в базу данных."""
        try:
            self.cursor.execute(
                """
                INSERT INTO personal_info (email, first_name, last_name, city)
                VALUES (?, ?, ?, ?)
            """,
                (
                    personal_info["email"],
                    personal_info["first_name"],
                    personal_info["last_name"],
                    personal_info["city"],
                ),
            )
            self.connection.commit()
            logger.info("Персональные данные сохранены в SQLite.")
        except Exception as e:
            logger.error(f"Ошибка при сохранении персональных данных: {e}")

    def save_wishlist_products(self, product_urls: List[str]) -> None:
        """Сохраняет ссылки на товары из избранного в базу данных."""
        try:
            for url in product_urls:
                self.cursor.execute(
                    """
                    INSERT OR IGNORE INTO wishlist_products (product_url)
                    VALUES (?)
                """,
                    (url,),
                )
            self.connection.commit()
            logger.info("Ссылки на товары из избранного сохранены в SQLite.")
        except Exception as e:
            logger.error(f"Ошибка при сохранении ссылок на товары: {e}")

    def save_product_details(self, product_details: Dict[str, Any]) -> None:
        """Сохраняет детали товара в базу данных."""
        try:
            self.cursor.execute(
                """
                INSERT INTO product_details (name, price_retail, price_wholesale, rating, reviews_count, stores_count)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    product_details["name"],
                    product_details["price_retail"],
                    product_details["price_wholesale"],
                    product_details["rating"],
                    int(product_details["reviews_count"]),
                    product_details["stores_count"],
                ),
            )
            product_id = self.cursor.lastrowid

            for review in product_details["reviews"]:
                self.cursor.execute(
                    """
                    INSERT INTO product_reviews (product_id, author, rating, date, message)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        product_id,
                        review["author"],
                        review["rating"],
                        review["date"],
                        review["message"],
                    ),
                )

            self.connection.commit()
            logger.info("Детали товара сохранены в SQLite.")
        except Exception as e:
            logger.error(f"Ошибка при сохранении деталей товара: {e}")

    def close(self) -> None:
        """Закрывает соединение с базой данных."""
        try:
            self.connection.close()
            logger.info("Соединение с SQLite закрыто.")
        except Exception as e:
            logger.error(f"Ошибка при закрытии соединения: {e}")


class JsonStorage(IStorage):
    def __init__(self, file_name: str = "siriust_data.json"):
        self.file_name = file_name
        self.data = {
            "personal_info": [],
            "wishlist_products": [],
            "product_details": [],
        }
        logger.info(f"Инициализировано JSON-хранилище: {self.file_name}")

    def save_personal_info(self, personal_info: Dict[str, str]) -> None:
        """Сохраняет персональные данные в JSON."""
        try:
            self.data["personal_info"].append(personal_info)
            self._save_to_file()
            logger.info("Персональные данные сохранены в JSON.")
        except Exception as e:
            logger.error(f"Ошибка при сохранении персональных данных: {e}")

    def save_wishlist_products(self, product_urls: List[str]) -> None:
        """Сохраняет ссылки на товары из избранного в JSON."""
        try:
            self.data["wishlist_products"].extend(product_urls)
            self._save_to_file()
            logger.info("Ссылки на товары из избранного сохранены в JSON.")
        except Exception as e:
            logger.error(f"Ошибка при сохранении ссылок на товары: {e}")

    def save_product_details(self, product_details: Dict[str, Any]) -> None:
        """Сохраняет детали товара в JSON."""
        try:
            self.data["product_details"].append(product_details)
            self._save_to_file()
            logger.info("Детали товара сохранены в JSON.")
        except Exception as e:
            logger.error(f"Ошибка при сохранении деталей товара: {e}")

    def _save_to_file(self) -> None:
        """Сохраняет данные в файл JSON."""
        try:
            with open(self.file_name, "w", encoding="utf-8") as file:
                json.dump(self.data, file, ensure_ascii=False, indent=4)
            logger.info(f"Данные сохранены в файл {self.file_name}.")
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных в файл: {e}")

    def close(self) -> None:
        """Закрывает хранилище (ничего не делает для JSON)."""
        logger.info("JSON-хранилище закрыто.")
