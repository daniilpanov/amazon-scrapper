from db_mongo import spec_db
from .reserve_async_collect_reviews import collect


def start(offset=0):
    all_top_phrases = spec_db('ai_highlights')['top_phrases'].find({'asin': 'B01JQZUMXY'}, sort=(('count', -1),), skip=offset)
    for keyword in all_top_phrases:
        keyword = keyword['phrase']
        print(keyword)  # last=towels they
        collect(None, None, 'B01JQZUMXY', keyword, 'amazon.com', 0, True)
