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
