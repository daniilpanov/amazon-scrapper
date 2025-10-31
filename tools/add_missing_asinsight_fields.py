from os import getenv

import certifi
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne
from pymongo.server_api import ServerApi


load_dotenv()

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
_map_country_code_to_marketplace_id = {v: k for k, v in _map_marketplace_id_to_country_code.items()}


def get_country_code(marketplace_id):
    return _map_marketplace_id_to_country_code.get(marketplace_id)


def get_marketplace_id(country_code):
    return _map_country_code_to_marketplace_id.get(country_code)

url = f"{getenv('MONGO_DB_HOST_SCHEMA')}://{getenv('MONGO_DB_USER')}:{getenv('MONGO_DB_PASS')}@{getenv('MONGO_DB_HOST')}"
with MongoClient(url, server_api=ServerApi('1'), username=getenv('MONGO_DB_USER'), password=getenv('MONGO_DB_PASS'), tlsCAFile=certifi.where()) as db:
    target_db = db["Asinsight"]
    source_collection = db["amazon_reports"]["catalog"]
    target_collections = [
        target_db["asin_info"],
        target_db["asin_variations"],
        target_db["asins_variations_flow_score"],
        target_db["asins_variations_status"],
        target_db["flow_trends"],
        target_db["research_asin_list"],
        target_db["search_terms_trends"],
    ]
    reverse_target_collections = [
        target_db["search_terms_top_asins"],
    ]

    # extract all needle data
    # Создаем словарь для быстрого поиска по паре (asin, country_code)
    catalog_dict = {
        (
            item["asin"], get_country_code(item["marketplace_id"])
        ): {
            "marketplace_id": item["marketplace_id"],
            "user_id": item.get("user_id")
        } for item in source_collection.find({}, projection={"asin": 1, "marketplace_id": 1, "user_id": 1})
    }

    # 1. Обновление target_collections - добавляем marketplace_id и user_id
    for collection in target_collections:
        # Находим все документы, в которых нет marketplace_id или user_id
        cursor = collection.find({
            "$or": [
                {"marketplace_id": {"$exists": False}},
                {"user_id": {"$exists": False}}
            ]
        })
        print("new collection", collection.name)
        ops = []

        for doc in cursor:
            asin = doc.get("asin")
            country_code = doc.get("country")

            if asin and country_code:
                key = asin, country_code
                if key in catalog_dict:
                    update_data = {}
                    if "marketplace_id" not in doc:
                        update_data["marketplace_id"] = catalog_dict[key]["marketplace_id"]
                    if "user_id" not in doc:
                        update_data["user_id"] = catalog_dict[key]["user_id"]

                    if update_data:
                        ops.append(UpdateOne(
                            {"_id": doc["_id"]},
                            {"$set": update_data}
                        ))
        print("start bulk write")
        if ops:
            collection.bulk_write(ops, ordered=False)
        print("end bulk write")
