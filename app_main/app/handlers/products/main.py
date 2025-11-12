import datetime

import pytz
from pymongo.errors import BulkWriteError

from ..abstract_handler import AbstractHandler
from ...models.products import ProductCard, ReviewsResultItem, AspectsResult


class ProductsHandler(AbstractHandler):
    @classmethod
    def get_handlers(cls):
        return {
            "result.product_card.success": {
                "handler": cls.set_product_result,
                "validator": ProductCard,
            },
            "result.product_reviews.success": {
                "handler": cls.set_reviews_result,
                "array_validator": ReviewsResultItem,
            },
            "result.product_aspects.success": {
                "handler": cls.set_aspects_result,
                "validator": AspectsResult,
            },
        }

    def _post_init(self):
        self._amazon_data_db = self._db["amazon_data"]
        self._amazon_reports_db = self._db["amazon_reports"]

    def set_reviews_result(self):
        self._data: list[ReviewsResultItem]

        try:
            self._amazon_data_db["customer_reviews"].insert_many(
                [model.model_dump() | {"scrap_datetime": datetime.datetime.now(pytz.UTC)} for model in self._data],
                ordered=False,
            )
        except BulkWriteError:
            pass

    def set_product_result(self):
        self._data: ProductCard

        if self._data.picture_url:
            main_uri, *_, ext = self._data.picture_url.rsplit(".", maxsplit=2)
            self._data.picture_url = main_uri + "." + ext
    
        if self._data.pictures_urls:
            sizing_pictures = []
            urls = self._data.pictures_urls
            self._data.pictures_urls = []

            for i, url in enumerate(filter(bool, urls)):
                main_uri, *_, ext = url.rsplit(".", maxsplit=2)
                self._data.pictures_urls.append(main_uri + "." + ext)
                variant = "MAIN" if not i else ("PT" + ("0" if i < 9 else "") + str(i))

                sizing_pictures.append({
                    "asin": self._data.asin,
                    "width": 1080, "height": 1080,
                    "marketplace_id": self._data.marketplaceId,
                    "user_id": "99376b43-3a2d-4994-a3cb-e712c1da35d1",
                    "variant": variant,
                    "link": main_uri + "._SM1080." + ext,
                })
                sizing_pictures.append({
                    "asin": self._data.asin,
                    "width": 550, "height": 550,
                    "marketplace_id": self._data.marketplaceId,
                    "user_id": "99376b43-3a2d-4994-a3cb-e712c1da35d1",
                    "variant": variant,
                    "link": main_uri + "._SX550." + ext,
                })
                sizing_pictures.append({
                    "asin": self._data.asin,
                    "width": 65, "height": 65,
                    "marketplace_id": self._data.marketplaceId,
                    "user_id": "99376b43-3a2d-4994-a3cb-e712c1da35d1",
                    "variant": variant,
                    "link": main_uri + "._SX65." + ext,
                })

            if sizing_pictures:
                try:
                    self._amazon_reports_db["catalog_images"].insert_many(
                        sizing_pictures,
                        ordered=False,
                    )
                except BulkWriteError:
                    pass
    
        data = {
            "product_url": "https://www.amazon.com/dp/" + self._data.asin,
            **self._data.model_dump(exclude={"aspects", "collectMedia"}),
            "parse_datetime": datetime.datetime.now(pytz.UTC)
        }
        self._amazon_data_db["product_self._data"].replace_one({"asin": self._data.asin}, data, upsert=True)

    def set_aspects_result(self):
        self._data: AspectsResult

        replace_aspects = []
        data = []
        for aspect in self._data.aspects:
            replace_aspects.append(aspect.Aspect)
            data.append(aspect.model_dump_with_asin(self._data.asin))

        try:
            self._amazon_data_db["aspects"].delete_many({"ASIN": self._data.asin, "Aspect": {"$in": replace_aspects}})
            self._amazon_data_db["aspects"].insert_many(data, ordered=False)
        except BulkWriteError:
            pass
