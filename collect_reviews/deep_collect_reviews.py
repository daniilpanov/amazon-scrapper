from database import spec_db
from .reserve_async_collect_reviews import collect

all_top_phrases = spec_db('ai_highlights')['top_phrases'].find({'asin': 'B01JQZUMXY'}, sort=('count', 1))
for keyword in all_top_phrases:
    collect(None, None, 'B01JQZUMXY', keyword, 'amazon.com', 0, True)
