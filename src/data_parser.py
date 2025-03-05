import logging
from typing import Any

import requests
from lxml import html

from interfaces import IDataParser

logger = logging.getLogger(__name__)


class DataParser(IDataParser):
    def __init__(self, session: requests.Session, base_url: str, headers: dict):
        self.session = session
        self.base_url = base_url
        self.headers = headers

    def get_personal_info(self) -> dict:
        profile_url = f"{self.base_url}/profiles-update"
        response = self.session.get(profile_url, headers=self.headers)
        if response.status_code == 200:
            tree = html.fromstring(response.content)
            personal_info = {
                "email": self._parse_email(tree),
                "first_name": self._parse_first_name(tree),
                "last_name": self._parse_last_name(tree),
                "city": self._parse_city(tree),
            }
            return personal_info
        else:
            logger.error(
                f"Ошибка при получении страницы профиля. Код статуса: {response.status_code}"
            )
            return {}

    def get_wishlist_products(self) -> list:
        wishlist_url = f"{self.base_url}/wishlist"
        response = self.session.get(wishlist_url, headers=self.headers)
        if response.status_code == 200:
            tree = html.fromstring(response.content)
            product_links = tree.xpath('//a[@class="product-title"]/@href')
            return [link for link in product_links]
        else:
            logger.error(
                f"Ошибка при получении страницы избранного. Код статуса: {response.status_code}"
            )
            return []

    def get_product_details(self, product_url: str) -> dict:
        response = self.session.get(product_url, headers=self.headers)
        if response.status_code == 200:
            tree = html.fromstring(response.content)

            return {
                "name": self._parse_product_name(tree),
                "price_retail": self._parse_price_retail(tree),
                "price_wholesale": self._parse_price_wholesale(tree),
                "rating": self._parse_rating(tree),
                "reviews_count": self._parse_reviews_count(tree),
                "stores_count": self._parse_stores_count(tree),
                "reviews": self._parse_reviews(tree),
            }
        else:
            logger.error(
                f"Ошибка при получении страницы товара. Код статуса: {response.status_code}"
            )
            return {}

    def _parse_email(self, tree: Any) -> str:
        return tree.xpath('//input[@id="email"]/@value')[0].strip()

    def _parse_first_name(self, tree: Any) -> str:
        return tree.xpath('//input[@id="elm_15"]/@value')[0].strip()

    def _parse_last_name(self, tree: Any) -> str:
        return tree.xpath('//input[@id="elm_17"]/@value')[0].strip()

    def _parse_city(self, tree: Any) -> str:
        return tree.xpath('//input[@id="elm_23"]/@value')[0].strip()

    def _parse_product_name(self, tree: Any) -> str:
        name = tree.xpath('//h1[@class="ty-product-block-title"]//bdi/text()')
        return name[0].strip() if name else "Нет названия"

    def _parse_price_retail(self, tree: Any) -> str:
        price_retail = tree.xpath(
            '//span[contains(@id, "sec_discounted_price")]/text()'
        )
        return price_retail[0].strip() if price_retail else "Нет цены"

    def _parse_price_wholesale(self, tree: Any) -> str:
        price_wholesale = tree.xpath('//span[contains(@id, "sec_second_price")]/text()')
        return price_wholesale[0].strip() if price_wholesale else "Нет цены"

    def _parse_rating(self, tree: Any) -> float:
        rating = tree.xpath(
            '//div[@class="ty-product-block__rating"]//i[contains(@class, "ty-icon-star")]'
        )
        total_rating = 0
        for star in rating:
            star_classes = star.get("class").split()
            if "ty-icon-star" in star_classes:
                total_rating += 1
            elif "ty-icon-star-half" in star_classes:
                total_rating += 0.5
        return total_rating

    def _parse_reviews_count(self, tree: Any) -> str:
        reviews_count = tree.xpath(
            '//a[contains(@class, "ty-discussion__review-a")]/text()'
        )
        return reviews_count[0].strip().split(" ", 1)[0] if reviews_count else "0"

    def _parse_stores_count(self, tree: Any) -> int:
        stores = tree.xpath(
            '//div[@id="content_features"]//div[@class="ty-product-feature"]'
        )
        stores_count = 0
        for store in stores:
            value = store.xpath('.//div[@class="ty-product-feature__value"]/text()')
            if value and "отсутствует" not in value[0].lower():
                stores_count += 1
        return stores_count

    def _parse_reviews(self, tree: Any) -> list:
        reviews = []
        for review in tree.xpath(
            '//div[contains(@class, "ty-discussion-post__content")]'
        ):
            author = review.xpath('.//span[@class="ty-discussion-post__author"]/text()')
            author = author[0].strip() if author else "Неизвестный автор"

            rating_stars = review.xpath('.//i[contains(@class, "ty-icon-star")]')
            rating_value = 0
            for star in rating_stars:
                star_classes = star.get("class").split()
                if "ty-icon-star" in star_classes:
                    rating_value += 1
                elif "ty-icon-star-half" in star_classes:
                    rating_value += 0.5

            date = review.xpath('.//span[@class="ty-discussion-post__date"]/text()')
            date = date[0].strip() if date else "Нет даты"

            message = review.xpath(
                './/div[@class="ty-discussion-post__message"]/text()'
            )
            message = " ".join([line.strip() for line in message if line.strip()])

            reviews.append(
                {
                    "author": author,
                    "rating": rating_value,
                    "date": date,
                    "message": message,
                }
            )
        return reviews
