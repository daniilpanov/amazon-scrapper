import requests

from ..helpers import hash_password


def get_token(session: requests.Session, email, password):
    res = session.post("https://api.asinsight.com/v2/system/login/emailChannel", json={
        "email": email,
        "password": hash_password(password),
        "resource": {},
    })
    if res.status_code != 200:
        return None

    return res.json()["token"]


def get_quota(session: requests.Session, token):
    res = session.get("https://api.asinsight.com/v2/account/assets/quota", headers={"Authorization": f"{token}"})
    if res.status_code != 200:
        return 0

    return res.json().get("quota", {}).get("asinResearch", 0)
