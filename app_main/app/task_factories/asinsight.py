from .abstract_factory import AbstractFactory
from ..models.asinsight import AsinSightTask

_map_marketplace_id_to_country_code = {
    "A2EUQ1WTGCTBG2": "CA",
    "ATVPDKIKX0DER": "US",
    "A1AM78C64UM0Y8": "MX",
    "A2Q3Y263D00KWC": "BR",
    "A28R8C7NBKEWEA": "IE",
    "A1RKKUPIHCS9HS": "ES",
    "A1F83G8C2ARO7P": "UK",
    "A13V1IB3VIYZZH": "FR",
    "AMEN7PMS3EDWL": "BE",
    "A1805IZSGTT6HS": "NL",
    "A1PA6795UKMFR9": "DE",
    "APJ6JRA9NG5V4": "IT",
    "A2NODRKZP88ZB9": "SE",
    "AE08WJ6YKNBMC": "ZA",
    "A1C3SOZRARQ6R3": "PL",
    "ARBP9OOSHTCHU": "EG",
    "A33AVAJ2PDY3EV": "TR",
    "A17E79C6D8DWNP": "SA",
    "A2VIGQ35RCS4UG": "AE",
    "A21TJRUUN4KGV": "IN",
    "A19VAU5U5O7RUS": "SG",
    "A39IBJ37TRP1C6": "AU",
    "A1VC38T7YXB528": "JP",
}


def _get_country_code(marketplace_id):
    return _map_marketplace_id_to_country_code.get(marketplace_id)


class AsinSightFactory(AbstractFactory):
    def publish_asinsight_tasks(self):
        catalog = self._db["amazon_reports"]["catalog"].find({}, projection={
            "asin": 1,
            "marketplace_id": 1,
            "user_id": 1,
        })
        messages_data = {(
            item["asin"],
            item["marketplace_id"],
            _get_country_code(item["marketplace_id"]),
            item.get("user_id"),
        ) for item in catalog}

        for message_data in messages_data:
            self._basic_publish(exchange="tasks", routing_key="asinsight", body=AsinSightTask(
                asin=message_data[0],
                marketplace_id=message_data[1],
                country=message_data[2],
                user_id=message_data[3],
            ))
