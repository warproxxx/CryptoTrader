import pandas as pd

from twitterscraper import Tweet
import requests
from bs4 import BeautifulSoup

class TestTweet:
    def find_between(self, s, first, last ):
        try:
            start = s.index( first ) + len( first )
            end = s.index( last, start )
            return s[start:end]
        except ValueError:
            return ""


    def setup_method(self):
        with open(__file__.replace(__file__.split("/")[-1], "") + "test.html") as myfile:
            self.html=myfile.read().replace('\n', '')

    def test_from_html(self):
        tweets = list(Tweet.from_html(self.html))
        assert(len(tweets) == 32)
        
        assert("<quoted_status>" in tweets[1].text)
        quoted_status = self.find_between(tweets[1].text, "<quoted_status>", "</quoted_status>")
        
        assert("New Blogpost:" and "https://medium.com/vanigplatform/the-state-of-cryptocurrency-market-in-2018-7ea693d85794" in quoted_status)
        assert(tweets[1].user == "dulmini_ayesha")
        assert(tweets[1].id == "1019112793205813250")
        assert(tweets[1].timestamp == "1531810398")
        assert("#vanig" in tweets[1].text)
        assert(tweets[1].replies == "0")
        assert(tweets[1].retweets == "0")
        assert(tweets[1].likes == "0")
        assert(tweets[1].reply_to_id == "1016973739404165120")
        assert(tweets[1].response_type == "quoted_retweet") 

        assert(tweets[0].response_type == "tweet")
        assert(tweets[0].reply_to_id == "0")

        assert(tweets[30].response_type == "quoted_retweet")
    
    def test_from_soup(self):
        response = requests.get("https://twitter.com/search?vertical=tweets&vertical=default&q=Bitcoin&l=EN", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36'})
        html = response.text

        soup = BeautifulSoup(html, "lxml")
        soups = soup.find_all('li', 'js-stream-item')

        tweets = []

        for tweetSoup in soups:
            tweets.append(Tweet.from_soup(tweetSoup))

        for tweet in tweets:
            assert(int(tweet.retweets) >= 0)
