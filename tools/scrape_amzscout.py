import json
import requests
from bs4 import BeautifulSoup

proxies = {"http": "http://amarpx:AmAscr3276O_@195.201.194.213:8118"}


def get_random_email():
    with requests.session() as sess:
        html = sess.get('https://tempmail.io/').text
        bs = BeautifulSoup(html, features='lxml')
        e = bs.find('input', {'id': 'email'})
        return e['value'] if e else None


def register(email):
    r = requests.post(
        f'https://amzscout.net/auth/v2/auth/registration?email={email.replace("@", "%40")}&software=LANDING',
        data="------WebKitFormBoundaryKM22TAH6hr3iq7NA\r\nContent-Disposition: form-data; name=\"action\"\r\n\r\nmessages\r\n------WebKitFormBoundaryKM22TAH6hr3iq7NA--\r\n",
        headers={
            "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryKM22TAH6hr3iq7NA",
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/536.36',
            'Referer': 'https://amzscout.net/authorization/?software=WEB'},
        proxies=proxies)
    return r


# try:
#     reg = register(get_random_email())
#     reg.raise_for_status()
#     default_token = reg.json()['hash']
# except:
#     default_token = 'M4gMsMCSj0yQjzABCxM1'
default_token = 'M4gMsMCSj0yQjzABCxM1'


def search(token=None, *, categories=None, minReviews=10, minEstRev=30000, maxRating=3.5,
           sortingField='createdDate', sortingDirection='', keywords=None):
    if not token:
        token = default_token
    if not categories:
        categories = ['2619525011', '2617941011', '15684181', '165796011', '3760911', '283155', '7141123011',
                      '4991425011', '172282', '16310101', '3760901', '1055398', '16310091', '133140011', '163856011',
                      '11091801', '1064954', '2972638011', '2619533011', '3375251', '228013', '165793011', '468642',
                      '0']
    url = 'https://amzscout.net/api/v1/COM/products?categoryIds=' + ('&categoryIds='.join(categories))
    if keywords:
        url += '&keywords=' + keywords

    r = requests.get(
        url + f'''&minReviews={minReviews}&minEstRev={minEstRev}&maxRating={maxRating}&domain=COM&pageSize=10&page=2&sortingField={sortingField}&sortingDirection={sortingDirection}''',
        headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Referer': 'https://amzscout.net/app/', 'X-Token': token},
        proxies=proxies)

    r.raise_for_status()

    return r.json()


data = []
asins = set()
all_kwds = ['wine cooler', 'teeth strips', 'whitening strips', 'heated blanket', 'coffee maker', 'coffee maker 12 cup',
            'fire tv stick', 'cooker', 'cooker pressure', 'rice cooker', 'teeth whitening strips']
kwds = []
for w in all_kwds:
    try:
        r = search(keywords=w)
        for i in r:
            old_l = len(asins)
            asins.add(i['asin'])
            if old_l < len(asins):
                data.append(i)
    except Exception as e:
        print(e)
        break
    kwds.append(w)
    print(r)

with open('amzscout-' + '-'.join(map(lambda i: str(i).replace(' ', '_'), kwds)) + '.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(data))
