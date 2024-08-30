from bs4 import BeautifulSoup
import pandas as pd

with open('tiktokussellers.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), features='lxml')
all_rows = soup.find_all('tr')
data = []
for row in all_rows:
    cells = row.find_all('td')
    profile_cell = cells[0]
    # video_cell = cells[1]
    gmv_cell = cells[2]
    items_sold_cell = cells[3]
    avg_video_views = cells[4]
    engagement_rate = cells[5]

    profile_avatar = profile_cell.select_one('[data-tid="m4b_avatar"] img').get('src')
    profile_data = profile_cell.select('div > span > div > div:not([data-tid="m4b_avatar"]) > span')

    profile_name, profile_description = profile_data[0].find_all('span', recursive=False)
    profile_name, *profile_tags = profile_name.find_all('span', recursive=False)
    profile_name = profile_name.text.strip()
    profile_description = profile_description.text.strip()
    profile_tags_str = []
    for tag in profile_tags:
        profile_tags_str.append(tag.text.strip())
    profile_tags = ', '.join(profile_tags_str)

    profile_categories = profile_data[1].find('span', recursive=False)
    profile_categories = profile_categories.text.strip()

    profile_followers = profile_data[2].find('span', recursive=False)
    profile_followers_count, profile_followers_gender, profile_followers_age = profile_followers.text.strip().split(', ')
    profile_followers_count = float(profile_followers_count[:-1] or '0')
    profile_followers_gender, profile_followers_gender_percents = profile_followers_gender.split(' ')
    profile_followers_gender_percents = float(profile_followers_gender_percents[:-1] or '0')

    data_item = {
        'Profile_name': profile_name,
        'Profile_description': profile_description,
        'Profile_tags': profile_tags,
        'Profile_categories': profile_categories,
        'Profile followers count, K': profile_followers_count,
        'Profile followers gender': profile_followers_gender,
        'Profile followers gender, %': profile_followers_gender_percents,
        'Profile followers age': profile_followers_age,
        'Profile_avatar': profile_avatar,
        'GMV, $K': float((gmv_cell.text.strip()[1:-1] or '0').replace(',', '')),
        'Items sold, K': float((items_sold_cell.text.strip()[:-1] or '0').replace(',', '')),
        'Avg. video views, K': float((avg_video_views.text.strip()[:-1] or '0').replace(',', '')),
        'Engagement rate, %': float((engagement_rate.text.strip()[:-1] or '0').replace(',', '')),
    }
    data.append(data_item)

df = pd.DataFrame(data)
df.to_csv('result.csv', index=False, encoding='utf-8')
