import logging

from interfaces import IAuth, IDataParser, IStorage

logger = logging.getLogger(__name__)


class SiriustParser:
    def __init__(self, auth: IAuth, data_parser: IDataParser, storage: IStorage):
        self.auth = auth
        self.data_parser = data_parser
        self.storage = storage

    def run(self):
        username = input("Введите логин: ")
        password = input("Введите пароль: ")
        if self.auth.login(username, password):
            personal_info = self.data_parser.get_personal_info()
            self.storage.save_personal_info(personal_info)
            logger.info("Персональные данные: %s", personal_info)

            product_links = self.data_parser.get_wishlist_products()
            if not product_links:
                logger.info("Нет товаров в избранном.")
                return
            self.storage.save_wishlist_products(product_links)

            for link in product_links:
                product_details = self.data_parser.get_product_details(link)
                if product_details:
                    logger.info("Название: %s", product_details["name"])
                    logger.info("Цена (розница): %s", product_details["price_retail"])
                    logger.info("Цена (опт): %s", product_details["price_wholesale"])
                    logger.info("Рейтинг: %s", product_details["rating"])
                    logger.info(
                        "Количество отзывов: %s", product_details["reviews_count"]
                    )
                    logger.info(
                        "Количество магазинов: %s", product_details["stores_count"]
                    )
                    logger.info("Отзывы: %s", product_details["reviews"])
                    logger.info("-" * 40)
                    self.storage.save_product_details(product_details)
