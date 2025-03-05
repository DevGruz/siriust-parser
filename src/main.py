import requests
import logging

from auth import Auth
from data_parser import DataParser
from siriust_parser import SiriustParser
from storages import SQLiteStorage, JsonStorage  # noqa: F401


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    session = requests.Session()
    base_url = "https://siriust.ru"
    headers = {"User-Agent": "Mozilla/5.0"}

    auth = Auth(session, base_url, headers)
    data_parser = DataParser(session, base_url, headers)
    
    storage_type = input("Выберите тип хранилища (sqlite/json): ").strip().lower()
    if storage_type == "sqlite":
        storage = SQLiteStorage()
    elif storage_type == "json":
        storage = JsonStorage()
    else:
        logger.error("Неверный тип хранилища. Используется JSON по умолчанию.")
        storage = JsonStorage()
        
    parser = SiriustParser(auth, data_parser, storage)
    parser.run()
    storage.close()
