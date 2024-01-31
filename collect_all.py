import datetime

import pandas as pd

import state
from collect_reviews import start_reviews_collect

print('Start time:', datetime.datetime.now().isoformat())
df = pd.read_csv('rew_test_top-phrases.csv', encoding='UTF-8')
df = df.drop_duplicates()
print(df)
print('Phrases loaded:', datetime.datetime.now().isoformat())
times = []

for i, item in df.iterrows():
    if state.get_asin(item['asin'], 'reviews') == -1:
        state.write_asin(item['asin'], 0, 'reviews')
    print('Phrase:', item['phrase'])
    start_time = datetime.datetime.now()
    print('Start time:', start_time)
    start_reviews_collect({'asin': item['asin'], 'keywords': item['phrase']})
    end_time = datetime.datetime.now()
    print('End time:', end_time)
    print('Delta: ', end_time - start_time)
    print('----------')
    times.append((end_time - start_time).total_seconds())
    state.write_asin(item['asin'], 0, 'reviews')


def from_seconds(secs: float):
    h = secs // 360
    m = secs % 360 // 60
    s = secs % 60 // 1
    return {'hours': h, 'minutes': m, 'seconds': s}


print('All deltas:', times)
print('Time spent:', from_seconds(sum(times)))
print('Median time per cycle iteration:', from_seconds(sum(times) / len(times)))
