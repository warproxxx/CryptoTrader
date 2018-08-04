from twitterscraper.query import twitterScraper

class TesttwitterScraper:
    def setup_method(self):
        self.ts = twitterScraper()

    def test_query_single_page(self):
        tweets, ids = self.ts.query_single_page("https://twitter.com/search?vertical=tweets&vertical=default&q=Bitcoin&l=EN")
        
        for tweet in tweets:
            assert(int(tweet.retweets) >= 0)
            assert(len(str(tweet.id)) >= 18)
            assert(int(tweet.likes) >= 0)
            assert(int(tweet.replies) >= 0)
            assert(tweet.reply_to_id)
            assert(any(x in tweet.response_type for x in ['tweet', 'retweet', 'quoted_status', 'quoted_retweet', 'reply']))
            assert(tweet.text)
            assert(len(str(tweet.timestamp)) >= 10)
            assert(len(tweet.user.split(' ')) == 1)

    def test_query_tweets_once(self):
        tweets = self.ts.query_tweets_once("Bitcoin", limit=10)

        for tweet in tweets:
            assert(int(tweet.retweets) >= 0)
            assert(len(str(tweet.id)) >= 18)
            assert(int(tweet.likes) >= 0)
            assert(int(tweet.replies) >= 0)
            assert(tweet.reply_to_id)
            assert(any(x in tweet.response_type for x in ['tweet', 'retweet', 'quoted_status', 'quoted_retweet', 'reply']))
            assert(tweet.text)
            assert(len(str(tweet.timestamp)) >= 10)
            assert(len(tweet.user.split(' ')) == 1)

    def test_query_historic_tweets(self):
        tweets = self.ts.query_historic_tweets("Bitcoin", limit=50)

        assert(len(tweets) >= 50)

        for tweet in tweets:
            assert(int(tweet.retweets) >= 0)
            assert(len(str(tweet.id)) >= 18)
            assert(int(tweet.likes) >= 0)
            assert(int(tweet.replies) >= 0)
            assert(tweet.reply_to_id)
            assert(any(x in tweet.response_type for x in ['tweet', 'retweet', 'quoted_status', 'quoted_retweet', 'reply']))
            assert(tweet.text)
            assert(len(str(tweet.timestamp)) >= 10)
            assert(len(tweet.user.split(' ')) == 1)