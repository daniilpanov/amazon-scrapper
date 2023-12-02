import os
import pandas as pd
import database


def export_asins(asins_list, user_id):
    data = database.db()['customer_reviews'].find({'asin': {'$in': asins_list}})
    print((data[0].keys() - ['_id']))
    df = pd.DataFrame(columns=data[0].keys() - ['_id'])
    for row in data:
        df.loc[len(df.index)] = row
    if not os.path.exists('tmp'):
        os.mkdir('tmp')
    path = os.path.join('tmp', str(hash(df.loc)) + '.csv')
    df.to_csv(path, index=False)
    with open(path, 'rb') as doc:
        pass
    os.remove(path)


export_asins(['B0BWL4ZDC8', 'B0BXFTSKC2'], 12345)
