from livescraper.query import MyStreamListener, query_tweets

import logging

class TestMyStreamListener():
    def setup_method(self):
        self.keywords = {'bitcoin': ['bitcoin', 'BTC'], 'dashcoin': ['dashcoin', 'DASH', 'darkcoin'], 'dogecoin': ['dogecoin', 'DOGE'], 'ethereum': ['ethereum', 'ETH'], 'litecoin': ['litecoin', 'LTC'], 'ripple': ['ripple', 'XRP'], 'monero': ['monero', 'XMR'], 'stellar': ['stellar', 'STR']}
        #what to set as logger?

    def test_on_status(self):
        pass

    def test_find_key(self):
        pass
    

class Testquery_tweets():
    def setup_method(self):
        pass
    
    def test_reply_to_id(self):
        pass

    def test_get_stream(self):
        pass

    def test_save_data(self):
        pass
    