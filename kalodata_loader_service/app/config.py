from hashlib import sha256

db_config = {
    'url': 'cluster0.tcwqk03.mongodb.net/?retryWrites=true&w=majority',
    'username': 'scrape_and_control',
    'password': 'kzy0obs6o4UDQWNY',
    'url_prefix': 'mongodb+srv',
}

API_KEY_HASH = sha256('b90502dc-97bf-11ef-972e-00090ffe0001')
