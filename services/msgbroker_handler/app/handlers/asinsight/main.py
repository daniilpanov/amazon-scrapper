import datetime
import functools
import json
import math
import time
from collections import defaultdict

import requests
from pymongo import ReplaceOne
from pymongo.errors import BulkWriteError, DuplicateKeyError

from .account.login_api import get_quota, get_token
from .account.main import register
from .gathering.api import AsinSightAPI
from ..abstract_handler import AbstractHandler
from ..exceptions import InvalidDataException, HandlerException


def _check_token(session, token):
    return get_quota(session, token) > 0


class AsinSightHandler(AbstractHandler):
    @property
    def handlers(self):
        return {"asinsight": {"handler": self.handle_start}}

    def handle_start(self, msg):
        start_time = time.time()

        data = json.loads(msg.decode())
        asin = data.get("asin")
        country = data.get("country", "US")
        additional_data = {
            "user_id": data.get("user_id"),
            "marketplace_id": data.get("marketplace_id"),
        }

        if not asin:
            raise InvalidDataException()

        with requests.Session() as session:
            new_token_callback = functools.partial(self._generate_new_token, session)
            asinsight_api = AsinSightAPI(session, asin, country, self._logger, new_token_callback)

            request_start_time = time.time()
            self._load_asin_info(asinsight_api, additional_data)
            self._logger.info(f"Request asin_info [{asin} ({country})] time: {time.time() - request_start_time}s")

            request_start_time = time.time()
            variation_id = self._load_variation_id(asinsight_api, additional_data)
            self._logger.info(f"Request variation_id [{asin} ({country})] time: {time.time() - request_start_time}s")

            request_start_time = time.time()
            self._load_variation_status(asinsight_api, variation_id, additional_data)
            self._logger.info(f"Request variation_status [{asin} ({country})] time: {time.time() - request_start_time}s")

            request_start_time = time.time()
            self._load_asin_flow_score(asinsight_api, additional_data)
            self._logger.info(f"Request asin_flow_score [{asin} ({country})] time: {time.time() - request_start_time}s")

            request_start_time = time.time()
            self._load_flow_score(asinsight_api, additional_data)
            self._logger.info(f"Request flow_score [{asin} ({country})] time: {time.time() - request_start_time}s")

            request_start_time = time.time()
            pages_scraped = self._research_list(asinsight_api, additional_data)
            request_time = time.time() - request_start_time
            if pages_scraped:
                self._logger.info(f"Request research_list [{asin} ({country})] time: {request_time}s ({request_time / pages_scraped}s per page)")

        end_time = time.time()
        self._logger.info(
            f"Full scraping of ASIN {asin} ({country}): {end_time - start_time}s"
            f"(started at {datetime.datetime.fromtimestamp(start_time)},"
            f"finished at {datetime.datetime.fromtimestamp(end_time)})"
        )

    def _generate_new_token(self, session):
        cursor = self._db["Asinsight"]["accounts"].find(sort=[("ts_created", -1)])
        for account in cursor:
            if _check_token(session, account["token"]):
                return account["token"]

            token = get_token(session, account["email"], account["password"])
            if _check_token(session, token):
                self._db["Asinsight"]["accounts"].update_one({"_id": account["_id"]}, {"$set": {"token": token}})
                return token

        account = register(session, self._logger)
        if not _check_token(session, account.token):
            raise HandlerException("Can not get token")

        self._db["Asinsight"]["accounts"].insert_one({
            "nickname": account.nickname,
            "email": account.email,
            "password": account.password,
            "token": account.token,
        })
        return account.token

    def _load_asin_info(self, asinsight_api, additional_data):
        country = asinsight_api.country

        data = asinsight_api.asin_info()
        asins_info = data.get("asins")
        if not asins_info:
            return False

        asin_info = asins_info[0]

        asin_info["country"] = country
        asin_info["priceDistributionDeal"] = asin_info["priceDistribution"]["deal"]
        asin_info["priceDistributionOriginPrice"] = asin_info["priceDistribution"]["originPrice"]
        asin_info["priceDistributionPrime"] = asin_info["priceDistribution"]["prime"]
        asin_info["ts_created"] = data["ts_created"]
        asin_info["date_created"] = data["date_created"]
        asin_info.update(additional_data)

        del asin_info["priceDistribution"]

        self._db["Asinsight"]["asin_info"].replace_one({
            "asin": asin_info["asin"],
            "country": country,
            "date_created": asin_info["date_created"],
        }, asin_info, upsert=True)
        return True

    def _load_variation_id(self, asinsight_api, additional_data):
        asin_variation_id = asinsight_api.asin_variation_id()
        if not asin_variation_id:
            return None

        self._db["Asinsight"]["asin_variations"].replace_one({
            "asin": asinsight_api.asin,
        }, {
            "asin": asinsight_api.asin,
            "variation_id": asin_variation_id,
        } | additional_data, upsert=True)
        return asin_variation_id

    def _load_variation_status(self, asinsight_api, variation_id, additional_data):
        asin_variation_status = asinsight_api.asin_variation_status(variation_id)
        asin_variation_status["asin"] = asinsight_api.asin
        asin_variation_status["country"] = asinsight_api.country
        self._db["Asinsight"]["asins_variations_status"].replace_one({
            "asin": asinsight_api.asin,
            "country": asinsight_api.country,
            "date_created": asin_variation_status["date_created"],
        }, asin_variation_status | additional_data, upsert=True)

    def _load_asin_flow_score(self, asinsight_api, additional_data):
        asin_variation_flow_score = asinsight_api.asin_variation_flow_score()
        ops = [ReplaceOne(
            {
                "asin": item["asin"],
                "country": item["country"],
                "date_created": asin_variation_flow_score["date_created"],
            },
            item | {
                "date_created": asin_variation_flow_score["date_created"],
                "ts_created": asin_variation_flow_score["ts_created"],
            } | additional_data,
            upsert=True,
        ) for item in asin_variation_flow_score.get("list", [])]

        self._db["Asinsight"]["asins_variations_flow_score"].bulk_write(ops, ordered=False)

    def _load_flow_score(self, asinsight_api, additional_data):
        flow_trends = asinsight_api.flow_trends()
        if not flow_trends.get("result") or not flow_trends["result"][0].get("xaxis"):
            return False

        dates = [datetime.datetime.fromisoformat(date) for date in flow_trends["result"][0]["xaxis"]]
        flow_trends_parsed = []
        flow_trends_data_keys = set(flow_trends["result"][0].keys()) - {"xaxis", "asin", "country", "total", "positionFlowScore"}

        for i in range(len(dates)):
            row = {
                "asin": asinsight_api.asin,
                "country": asinsight_api.country,
                "date_created": dates[i],
                "ts_created": datetime.datetime.now(),
            } | additional_data

            for key in flow_trends_data_keys:
                row[key] = flow_trends["result"][0][key][i]
            flow_trends_parsed.append(row)

        old_data = list(self._db["Asinsight"]["flow_trends"].find({
            "asin": asinsight_api.asin,
            "country": asinsight_api.country,
            "date_created": {"$in": dates},
        }))
        # TODO: replace it with something more careful
        self._db["Asinsight"]["flow_trends"].delete_many({"_id": {"$in": [item["_id"] for item in old_data]}})

        try:
            self._db["Asinsight"]["flow_trends"].insert_many(flow_trends_parsed, ordered=False)
            return True
        except:
            self._db["Asinsight"]["flow_trends"].insert_many(old_data, ordered=False)
            self._logger.exception("Failed to load asinsight flow trends")
            return False

    def _research_list(self, asinsight_api, additional_data):
        research_result = asinsight_api.research_asin_list()
        if not research_result or not research_result.get("total"):
            self._logger.warning(f"No research result for asin {asinsight_api.asin} ({asinsight_api.country})")
            self._logger.debug(f"Response: {str(research_result)}")
            return 0

        research_timestamp = research_result["ts_created"]
        research_date = research_result["date_created"]
        research_pages_to_parsing = math.ceil(research_result["total"] / research_result["pageSize"]) + 1
        top_100_results_pages_count = math.ceil(100 / research_result["pageSize"])

        for page in range(2, research_pages_to_parsing + 1):
            page_results = []
            terms = []

            for item in research_result.get("list", []):
                item["ts_created"] = research_timestamp
                item["date_created"] = research_date
                item["search_term"] = item["searchTerm"]
                terms.append(item["searchTerm"])
                del item["searchTerm"]
                item.update(additional_data)
                page_results.append(item)

            try:
                self._db["Asinsight"]["research_asin_list"].insert_many(page_results, ordered=False)
            except (DuplicateKeyError, BulkWriteError):
                pass

            self._load_search_term_trends(asinsight_api, terms, additional_data)
            self._load_search_term_top_asins(asinsight_api, terms)

            if page <= top_100_results_pages_count:
                self._load_search_terms_rank_trends_daily(asinsight_api, terms, page)

            if page < research_pages_to_parsing:
                research_result = asinsight_api.research_asin_list(page)

        return research_pages_to_parsing

    def _load_search_term_trends(self, asinsight_api, search_terms, additional_data):
        trends = asinsight_api.search_terms_trends(search_terms)
        if not trends:
            return False

        flat_trends = []
        for item in trends.get("searchTerms", []):
            search_term = item["searchTerm"]
            trend = item["trends"]
            del trend["xaxis"]
            keys = set(trend.keys()) - {"searchTerm", "country", "reportFromDate", "reportToDate"}

            for i in range(len(trend["reportFromDate"])):
                row = {
                    "asin": asinsight_api.asin,
                    "country": asinsight_api.country,
                    "search_term": search_term,
                    "report_from": datetime.datetime.fromisoformat(trend["reportFromDate"][i]),
                    "report_to": datetime.datetime.fromisoformat(trend["reportToDate"][i]),
                } | additional_data
                for key in keys:
                    row[key] = trend[key][i]

                flat_trends.append(row)

        try:
            self._db["Asinsight"]["search_terms_trends"].insert_many(flat_trends, ordered=False)
        except (DuplicateKeyError, BulkWriteError):
            pass

        return True

    def _load_search_term_top_asins(self, asinsight_api, search_terms):
        top_asins = asinsight_api.search_terms_top_asins(search_terms)
        if not top_asins:
            return False

        flat_top_asins = []
        for search_term_item in top_asins.get("searchTerms", []):
            if not search_term_item:
                continue

            search_term = search_term_item.get("searchTerm")
            report_from = search_term_item.get("reportFromDate")
            report_to = search_term_item.get("reportToDate")
            if not search_term or not report_from or not report_to:
                continue

            report_from = datetime.datetime.fromisoformat(report_from)
            report_to = datetime.datetime.fromisoformat(report_to)

            for top_asin in search_term_item.get("topAsins", []):
                top_asin["search_term"] = search_term
                top_asin["report_from"] = report_from
                top_asin["report_to"] = report_to
                flat_top_asins.append(top_asin)

        try:
            self._db["Asinsight"]["search_terms_top_asins"].insert_many(flat_top_asins, ordered=False)
        except (DuplicateKeyError, BulkWriteError):
            pass

        return True

    def _load_search_terms_rank_trends_daily(self, asinsight_api, search_terms, additional_data):
        for search_term in search_terms:
            result = asinsight_api.search_terms_rank_trends_daily(search_term).get("entities")
            if not result:
                continue

            data = result[0]
            if not data or "trends" not in data:
                continue

            trends = data["trends"]
            documents = []
            for item in trends:
                date = datetime.datetime.fromisoformat(item["localDate"])
                positions = {}
                for position_type, position_description in item.get("displayPositions", {}).items():
                    positions[position_type] = position_description.get("totalRank")
                documents.append({
                    "asin": asinsight_api.asin,
                    "country": asinsight_api.country,
                    "search_term": search_term,
                    "date_created": date,
                    "ts_created": time.time(),
                } | additional_data | positions)

            try:
                self._db["Asinsight"]["search_terms_rank_trends_daily"].insert_many(documents, ordered=False)
            except (DuplicateKeyError, BulkWriteError):
                pass

        return True


handler = AsinSightHandler
