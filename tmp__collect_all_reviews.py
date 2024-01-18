import pandas as pd

import state
from collect_reviews import start_reviews_collect

df = pd.read_csv('TMP__top_phrases.csv', encoding='UTF-8')
df = df.drop('_id', axis=1)
df = pd.concat([df, pd.read_csv('TMP__top_phrases2.csv', encoding='UTF-8')], ignore_index=True)
df = df.drop_duplicates()
print(df)

for i, item in df.iterrows():
    if state.get_asin(item['asin'], 'reviews') == -1:
        state.write_asin(item['asin'], 0, 'reviews')
    print(item['phrase'])
    start_reviews_collect({'asin': item['asin'], 'keywords': item['phrase']})
    state.write_asin(item['asin'], 0, 'reviews')
