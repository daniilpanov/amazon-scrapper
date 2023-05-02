import os
from time import sleep

from pandas import DataFrame

from initialization import initialize
from configuration import FOLDER_NAME, State, get_file_write_mode

st = State('feedback__state.dat')
marketplaceID = None
if st.has_data():
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

selenium = initialize()

# https://www.amazon.com/sp?ie=UTF8&seller=ANLM9VGDHWW4V
selenium.get("https://www.amazon.com/sp?ie=UTF8&seller=" + seller)
selenium.execute_script("""
var jq = document.createElement('script');
jq.src = "https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js";
document.getElementsByTagName('head')[0].appendChild(jq);
""")
sleep(1)

if not st.has_data():
    marketplaceID = selenium.execute_script("return ue_mid")
    st['seller'] = seller
    st['marketplaceID'] = marketplaceID
    st.write()

for rating in range(start_rating, 6):
    st['rating'] = rating
    st.write()
    data = DataFrame()
    for page in range(start_page, 101):
        st['page'] = page
        st['got'] = 0
        st.write()
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
            mode=get_file_write_mode('feedback.csv'),
            header=get_file_write_mode('feedback.csv') == 'w',
        )
        st['got'] = 1
        st.write()
    start_page = 0


selenium.close()
