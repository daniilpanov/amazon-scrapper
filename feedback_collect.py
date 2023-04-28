import os
from time import sleep

from pandas import DataFrame
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import OperatingSystem, SoftwareName

from config import WEBDRIVER_PATH, HEADLESS, state, get_file, FOLDER_NAME

st = state(filename='feedback__state.dat')
marketplaceID = None
if st:
    seller = st['seller']
    marketplaceID = st['marketplaceID']
    start_rating = int(st['rating'])
    start_page = int(st['page'])
    if st['got'] == "1":
        start_page += 1
else:
    seller = input("Please, input seller ID: ")
    start_rating = 1
    start_page = 0

options = webdriver.ChromeOptions()
options.add_argument('--window-size=1920,1080')
options.add_argument('--start-maximized')
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)
if HEADLESS:
    options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
options.add_argument(
    f'user-agent={UserAgent(software_names=(SoftwareName.CHROME.value,), operating_systems=(OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value), limit=120).get_random_user_agent()}'
)
options.add_argument('--ignore-certificate-errors-spki-list')
options.add_argument('--ignore-ssl-errors')

selenium = WebDriver(WEBDRIVER_PATH, options=options)

# https://www.amazon.com/sp?ie=UTF8&seller=ANLM9VGDHWW4V
selenium.get("https://www.amazon.com/sp?ie=UTF8&seller=" + seller)
selenium.execute_script("""
var jq = document.createElement('script');
jq.src = "https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js";
document.getElementsByTagName('head')[0].appendChild(jq);
""")
sleep(1)

if not st:
    marketplaceID = selenium.execute_script("return ue_mid")
    state(filename='feedback__state.dat', seller=seller, marketplaceID=marketplaceID)

for rating in range(start_rating, 6):
    state(filename='feedback__state.dat', rating=rating)
    data = DataFrame()
    for page in range(start_page, 101):
        state(filename='feedback__state.dat', page=page, got=0)
        res = selenium.execute_script("""
        var a = $.post(
            "https://www.amazon.com/sp/ajax/feedback",
            {
                seller: '""" + seller + """',
                marketplaceID: '""" + str(marketplaceID) + """',
                pageNumber: """ + str(page) + """,
                toRating: """ + str(rating) + """,
                fromRating: """ + str(rating) + """,
                timePeriod: "Lifetime",
            },
        );
        return a;
        """)
        d = res['details']
        raw_data = []
        for item in d:
            raw_data.append({
                'rating': item['rating'],
                'text': item['ratingData']['text']['expandedText'],
                'rater': item['rater'],
                'rater_profile_link': item['raterProfileUrl'],
                'date': item['ratingData']['date'],
                'was_suppressed': item['ratingData']['wasSuppressed'],
                'suppress_reason': item['ratingData']['suppressReasonText'],
            })
        new_data = DataFrame(
            raw_data,
            columns=['rating', 'text', 'rater', 'rater_profile_link', 'date', 'was_suppressed', 'suppress_reason'],
        )
        if new_data.equals(data):
            break
        data = new_data
        new_data.to_csv(
            os.path.join(FOLDER_NAME, 'feedback.csv'),
            index=False,
            mode=get_file('feedback.csv'),
            header=get_file('feedback.csv') == 'w',
        )
        state(filename='feedback__state.dat', got=1)
    start_page = 0


selenium.close()
