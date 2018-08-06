from twitterscraper.query import twitterScraper, query_historic_tweets

from libs.reading_utils import get_keywords, get_custom_keywords
from libs.writing_utils import get_locations, get_logger

import datetime


class TesttwitterScraper:
    def setup_method(self):
        self.ts = twitterScraper()

    def test_query_single_page(self):
        tweets, ids = self.ts.query_single_page("https://twitter.com/search?vertical=tweets&vertical=default&q=Bitcoin&l=EN")
        
        for tweet in tweets:
            assert(int(tweet.retweets) >= 0)
            # assert(len(str(tweet.id)) >= 18)
            assert(int(tweet.likes) >= 0)
            assert(int(tweet.replies) >= 0)
            # assert(tweet.reply_to_id)
            assert(any(x in tweet.response_type for x in ['tweet', 'retweet', 'quoted_status', 'quoted_retweet', 'reply']))
            # assert(tweet.text)
            # assert(len(str(tweet.timestamp)) >= 10)
            assert(len(tweet.user.split(' ')) == 1)

    def test_query_tweets_once(self):
        tweets = self.ts.query_tweets_once("Bitcoin", limit=10)

        for tweet in tweets:
            assert(int(tweet.retweets) >= 0)
            # assert(len(str(tweet.id)) >= 18)
            assert(int(tweet.likes) >= 0)
            assert(int(tweet.replies) >= 0)
            # assert(tweet.reply_to_id)
            assert(any(x in tweet.response_type for x in ['tweet', 'retweet', 'quoted_status', 'quoted_retweet', 'reply']))
            # assert(tweet.text)
            # assert(len(str(tweet.timestamp)) >= 10)
            assert(len(tweet.user.split(' ')) == 1)

    def test_query_tweets(self):
        tweets = self.ts.query_tweets("Bitcoin", limit=50)

        assert(len(tweets) >= 50)

        for tweet in tweets:
            assert(int(tweet.retweets) >= 0)
            # assert(len(str(tweet.id)) >= 18)
            assert(int(tweet.likes) >= 0)
            assert(int(tweet.replies) >= 0)
            # assert(tweet.reply_to_id)
            assert(any(x in tweet.response_type for x in ['tweet', 'retweet', 'quoted_status', 'quoted_retweet', 'reply']))
            # assert(tweet.text)
            # assert(len(str(tweet.timestamp)) >= 10)
            assert(len(tweet.user.split(' ')) == 1)

class Testquery_historic_tweets():
    def setup_method(self):
        liveKeywords, _ = get_keywords(keywordsFile="/twitterscraper/tests/keywords.json")
        historicList = get_custom_keywords(liveKeywords, datetime.datetime(2018, 1, 1, 2, 2 , 2), datetime.datetime(2018, 1, 3, 3, 3, 3))

        _, self.currRoot_dir = get_locations()
        self.logger = get_logger(self.currRoot_dir + '/twitterscraper/tests/scrape.log')
        self.qh = query_historic_tweets(historicList, logger=self.logger)
        

    def test_scrape(self):
        dic = self.qh.scrape(start_date_time=datetime.datetime(2018,1,1,1,1,1), end_date_time=datetime.datetime(2018,1,2,2,2,2), proxy=None, form="return", keyword="Bitcoin or BTC", coinname="Bitcoin")
        print(dic)

    def test_perform_search(self):
        all_data = self.qh.perform_search(form="return")
        print(all_data)