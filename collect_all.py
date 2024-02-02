import datetime

import pandas as pd
from concurrent.futures import ProcessPoolExecutor



def col(item):
    try:
        from collect_reviews import start_reviews_collect
        print('Phrase:', item['phrase'])
        start_time = datetime.datetime.now()
        print('Start time:', start_time)
        start_reviews_collect({'asin': item['asin'], 'keywords': item['phrase']})
        end_time = datetime.datetime.now()
        print('End time:', end_time)
        print('Delta: ', end_time - start_time)
        print('----------')
    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    print('Start time:', datetime.datetime.now().isoformat())
    df = pd.read_csv('rew_B079RLZSYL_top-phrases.csv', encoding='UTF-8')
    df = df.drop_duplicates()
    print(df)
    with ProcessPoolExecutor(max_workers=2) as pool:
        try:
            all_start_time = datetime.datetime.now()
            print('Phrases loaded, pool created:', all_start_time.isoformat())
            pool.map(col, [item for i, item in df.iterrows()])
            pool.shutdown(True)
        except KeyboardInterrupt:
            pass

    all_end_time = datetime.datetime.now()
    print('End time:', all_end_time.isoformat())
    print('Time spent:', (all_end_time - all_start_time))
