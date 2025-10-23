import datetime
import logging
import time

import requests
from requests.exceptions import RequestException, ConnectionError as RequestConnectionError


class AsinSightAPI:
    base_url = "https://api.asinsight.com/v2/"

    def __init__(self, session: requests.Session, auth_token: str, asin: str, country: str, logger: logging.Logger):
        self.session = session
        self.auth_token = auth_token
        self.asin = asin
        self.country = country
        self.logger = logger

        if not session.headers.get("Authorization"):
            self.session.headers["Authorization"] = auth_token

    def asin_variation_id(self) -> str:
        """
        Endpoint: /v2/asins/variations
        Priority 1

        Schema: {
          "variationId": "9966b555-d8bf-47ce-8d35-317e6e5ebd83"
        }

        :return:
        """
        return (self._make_request("POST", "asins/variations", self._generate_payload()) or {}).get("variationId")

    def asin_variation_flow_score(self) -> dict:
        """
        Endpoint: /v2/asins/variations/flowScore
        Priority 2

        Schema: {
          "list": [
            {
              "title": "Nature's Bounty Optimal Solutions Hair, Skin & Nails Vitamin Gummies with Biotin, 2500 mcg, Strawberry, 80 Count, 40 Total Servings",
              "picUrl": "https://m.media-amazon.com/images/I/7179yGpT0pL._AC_UL320_.jpg",
              "price": 7.880000114440918,
              "currency": "USD",
              "stars": 4.699999809265137,
              "ratings": 66317,
              "asin": "B00G36TJKW",
              "country": "US",
              "amazonUrl": "https://www.amazon.com/dp/B00G36TJKW",
              "score": 4144,
              "lastWeekScore": 2693,
              "scoreRatio": 0.39261013737565137,
              "scoreGrowthRatio": 0.538804292678833,
              "natureFlowScore": 4144,
              "lastWeekNatureFlowScore": 2693,
              "natureFlowScoreRatio": 1,
              "natureScoreGrowthRatio": 0.538804292678833,
              "adFlowScore": 0,
              "lastWeekAdFlowScore": 0,
              "adFlowScoreRatio": 0,
              "adScoreGrowthRatio": 0,
              "sales": 4000,
              "salesRatio": 0.3076923076923077
            },
            ...
          ],
          "total": 0,  // ??
          "found": 0,  // ??
          "notFound": 0  // ??
        }

        :return:
        """
        return self._make_request(
            "POST",
            "asins/variations/flowScore",
            self._generate_payload(as_array=True),
        )

    def asin_variation_status(self, variation_id: str) -> dict:
        """
        Endpoint: /v2/asins/variations/status
        Priority 2

        Schema: {
          "parentAsin": "",
          "childAsins": null,
          "variantStatus": "Submitted",
          "lastUpdatedTime": null,
          "renewAvailable": null,
          "variationValues": null,
          "asinVariationValues": null,
          "correspondence": {}
        }

        :param variation_id:
        :return:
        """
        return self._make_request(
            "POST",
            "asins/variations/status",
            self._generate_payload(additional_payload={
                "variationId": variation_id,
            }, override_payload=True),
        )

    def asin_info(self) -> dict:
        """
        Endpoint: /v2/asins/info
        Priority 1

        Schema: {
          "asins": [
            {
              "country": "US",
              "asin": "B07BHTJ4B9",
              "amazonUrl": "https://www.amazon.com/dp/B07BHTJ4B9",
              "picUrl": "https://m.media-amazon.com/images/I/61d1L158XtL._AC_UY128_.jpg",
              "bigPicUrl": "https://m.media-amazon.com/images/I/61d1L158XtL._AC_UY512_.jpg",
              "currency": "USD",
              "price": 9.1899995803833,
              "ratings": 66317,
              "stars": 4.699999809265137,
              "title": "Nature's Bounty Hair, Skin & Nails with ...",
              "sales": 5000,
              "priceDistribution": {
                "deal": false,
                "originPrice": 15.989999771118164,
                "prime": null
              },
              "bestSeller": null
            }
          ]
        }

        :return:
        """
        return self._make_request("POST", "asins/info", self._generate_payload(as_array=True))

    def flow_trends(self, start_date: str = "", end_date: str = "") -> dict:
        """
        Endpoint: /v2/asins/flow/trends
        Priority 1

        Schema: {
          "result": [
            {
              "country": "US",
              "asin": "B07BHTJ4B9",
              "total": 90,
              "xaxis": [
                "2025-07-15",
                ...
              ],
              "natureFlowScore": [
                {
                  "value": 319,
                  "ratio": 1
                },
                ...
              ],
              "adFlowScore": [
                {
                  "value": 0,
                  "ratio": 0
                },
                ...
              ],
              "totalFlowScore": [
                319,
                ...
              ],
              "natureSearchTermNum": [
                318,
                ...
              ],
              "adSearchTermNum": [
                0,
                ...
              ],
              "totalSearchTermNum": [
                318,
                ...
              ],
              "positionFlowScore": {
                ### TEMPLATE ###
                "<name>FlowScore": (null | {"value": <number>, "ratio": <number>})
                keys:
                "naFlowScore"
                "spFlowScore"
                "erFlowScore"
                "acFlowScore"
                "orFlowScore"
                "sbFlowScore"
                "sbvFlowScore"
                "oorFlowScore"
                "sorFlowScore"
                "hrFlowScore"
                "trbFlowScore"
                "cpfFlowScore"
              }
            }
          ],
          "total": 1
        }

        :param start_date:
        :param end_date:
        :return:
        """
        return self._make_request(
            "POST",
            "asins/flow/trends",
            self._generate_payload(as_array=True, array_key="entities", additional_payload={
                "startDate": start_date,
                "endDate": end_date,
            }),
        )

    def research_asin_list(self, page: int = 1, page_size: int = 50) -> dict:
        """
        Endpoint: /v2/asins/research/list
        Priority 0

        Schema: {
          "list": [
            {
              "country": "US",
              "asin": "B07BHTJ4B9",
              "searchTerm": "hair skin and nails vitamins",
              "following": false,
              "weekFlow": 12810,
              "weekFlowRatio": 0.08645183,
              "weekFlowGrowthRatio": -0.003965477,
              "naRank": {
                "totalRank": 6,
                "page": 1,
                "pageRank": 6,
                "snapshotDate": 1760328155,
                "rankDiff": 0,
                "isNew": false
              },
              "spRank": {
                "totalRank": null,
                "page": 0,
                "pageRank": 0,
                "snapshotDate": -62135596800,
                "rankDiff": 0,
                "isNew": false
              },
              "displayPosExtend": [
                ### TEMPLATE ###
                {"label": "<name>", "freshness": "<week | overMonth>"}

                "na", "sp", "sb", "sbv", "ac", "er", "hr", "trb", "cpf", "oor", "sor", "or", "sd"
              ],
              "searchFrequencyRank": 6169,
              "weeklySearchVolume": 21742,
              "natureRatio": 1,
              "adRatio": 0,
              "natureFlow": 12810,
              "adFlow": 0,
              "flows": {
                "weekFlow": 12810,
                "natureFlow": 12810,
                "adFlow": 0,
                "flowDistribution": {
                  "nature": 1,
                  "ad": 0
                },
                "weekFlowRatio": 0.08645183,
                "weekFlowGrowthRatio": -0.003965477,
                "adFlowRatio": 0,
                "adFlowGrowthRatio": 0,
                "natureFlowRatio": 0.08645183,
                "natureFlowGrowthRatio": -0.003965477,
                "adDistribution": {
                  "sp": null,
                  "sb": null,
                  "sbv": null,
                  "sor": null,
                  "hr": null,
                  "trb": null,
                  "cpf": null
                },
                "natureDistribution": {
                  "na": 1,
                  "ac": null,
                  "er": null,
                  "oor": null,
                  "cpf": null
                },
                "positionFlowDistribution": {
                  "sp": null,
                  "sb": null,
                  "sbv": null,
                  "sor": null,
                  "hr": null,
                  "trb": null,
                  "na": 1,
                  "ac": null,
                  "er": null,
                  "oor": null,
                  "cpf": null
                },
                "flowRank": 0
              },
              "flowPeriod": null
            },
            ...
          ],
          "total": 716,
          "page": 1,
          "pageSize": 50,
          "flowPeriodSummary": {
            "total": 8,
            "detail": {
              "lost": {
                "value": 1,
                "valueChange": 1
              },
              "new": {
                "value": 4,
                "valueChange": 4
              },
              "increase": {
                "value": 3,
                "valueChange": 3
              },
              "decrease": {
                "value": 0,
                "valueChange": 0
              }
            }
          }
        }

        :param page:
        :param page_size:
        :return:
        """
        return self._make_request(
            "POST",
            "asins/research/list",
            self._generate_payload(additional_payload={
                "page": page,
                "pageSize": page_size,
                "query": "",
                "orders": [{"field": "follow", "order": "desc"}],
                "filters": [],
                "rangeFilters": [],
            }),
        )

    def search_terms_trends(self, search_terms: list[str], weeks: int = 12):
        """
        Endpoint: /v2/searchTerms/trends
        Priority 1

        Schema: {
          "searchTerms": [
            {
              "country": "US",
              "searchTerm": "hair skin and nails vitamins",
              "values": {
                "searchFrequencyRank": 6169,
                "weekSearch": 21742,
                "clickShare": 0.4254,
                "conversionShare": 0.3963
              },
              "trends": {
                "xaxis": [
                  "07/13-07/19",
                  ...
                ],
                "searchFrequencyRank": [
                  6162,
                  ...
                ],
                "weekSearch": [
                  21762,
                  ...
                ],
                "clickShare": [
                  0.505,
                  ...
                ],
                "conversionShare": [
                  0.4523,
                  ...
                ],
                "reportFromDate": [
                  "2025-07-13",
                  ... (ISO dates)
                ],
                "reportToDate": [
                  "2025-07-19",
                  ... (ISO dates)
                ]
              }
            },
            ...
          ]
        }

        :param search_terms:
        :param weeks:
        :return:
        """

        data = self._generate_payload(no_biz=True)
        data["biz"] = {
            "searchTerms": [{"country": self.country, "searchTerm": search_term} for search_term in search_terms],
            "weeks": weeks,
        }

        return self._make_request("POST", "searchTerms/trends", data)

    def search_terms_top_asins(self, search_terms: list[str]) -> dict:
        """
        Endpoint: /v2/searchTerms/topAsins
        Priority 2

        Schema: {
          "searchTerms": [
            {
              "country": "US",
              "searchTerm": "hair skin and nails vitamins",
              "reportFromDate": "2025-09-28",
              "reportToDate": "2025-10-04",
              "topAsins": [
                {
                  "country": "US",
                  "asin": "B0072F8D7S",
                  "picUrl": "https://m.media-amazon.com/images/I/61IkMUgpBWL._AC_UL320_.jpg",
                  "bigPicUrl": "https://m.media-amazon.com/images/I/61IkMUgpBWL._AC_UY512_.jpg",
                  "price": 9.19,
                  "ratings": 61957,
                  "stars": 4.5,
                  "currency": "USD",
                  "amazonUrl": "https://www.amazon.com/dp/B0072F8D7S",
                  "clickShare": 0.2929,
                  "conversionShare": 0.3004
                },
                ... (2 more)
              ]
            },
            ...
          ]
        }

        :param search_terms:
        :return:
        """
        data = self._generate_payload(no_biz=True)
        data["biz"] = {
            "searchTerms": [{"country": self.country, "searchTerm": search_term} for search_term in search_terms],
        }

        return self._make_request("POST", "searchTerms/topAsins", data)

    def _generate_payload(
        self, *,
        as_array: bool = False,
        array_key = "asins",
        additional_payload: dict | None = None,
        override_payload: bool = False,
        no_biz = False,
    ) -> dict:
        return {
            "resource": {
                "country": self.country,
                "asin": self.asin,
            },
            "biz": (
                {} if no_biz else ({
                    array_key: [
                        (
                            {} if override_payload
                            else {
                                "asin": self.asin,
                                "country": self.country,
                            }
                        ) | (additional_payload or {}),
                    ],
                } if as_array else (
                    (
                        {} if override_payload
                        else {
                            "asin": self.asin,
                            "country": self.country,
                        }
                    ) | (additional_payload or {})
                ))
            ),
        }

    def _make_request(self, method: str, endpoint: str, data: dict = None, *, retries_left=10) -> dict:
        url = f"{self.base_url}{endpoint}"
        self.logger.debug(f"Request: {method} {url} with {str(data)}")
        response = None

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
            )
            response.raise_for_status()
            data = response.json()
            data["ts_created"] = time.time()
            data["date_created"] = datetime.datetime.combine(datetime.date.today(), datetime.time())
            return data
        except RequestConnectionError:
            self.logger.exception("Request connection error. Retrying")
            if retries_left <= 0:
                raise

            time.sleep(1)
            return self._make_request(method, endpoint, data, retries_left=retries_left - 1)
        except RequestException as e:
            self.logger.exception(f"Error on request [{method} /{endpoint}]: {e}\nData: {data}")
            if response:
                self.logger.debug(f"Request headers: {str(response.request.headers)}")
            raise
