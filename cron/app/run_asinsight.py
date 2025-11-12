import json

import pika
from pymongo import MongoClient

from marketplace_id_translator import get_country_code


def run_asinsight(conn: MongoClient, rabbit: pika.BlockingConnection):
    catalog = conn["amazon_reports"]["catalog"].find({}, projection={"asin": 1, "marketplace_id": 1, "user_id": 1})
    messages_data = {(
        item["asin"],
        item["marketplace_id"],
        get_country_code(item["marketplace_id"]),
        item.get("user_id"),
    ) for item in catalog}

    with rabbit.channel() as channel:
        for message_data in messages_data:
            channel.basic_publish(exchange="tasks", routing_key="asinsight", body=json.dumps({
                "asin": message_data[0],
                "marketplace_id": message_data[1],
                "country": message_data[2],
                "user_id": message_data[3],
            }).encode("utf-8"))
