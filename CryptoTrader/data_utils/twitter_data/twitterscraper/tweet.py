from datetime import datetime

from bs4 import BeautifulSoup
from coala_utils.decorators import generate_ordering


@generate_ordering('timestamp', 'id', 'text', 'user', 'replies', 'retweets', 'likes', 'reply_to_id')
class Tweet:
    def __init__(self, user, fullname, id, url, timestamp, text, replies, retweets, likes, html, reply_to_id):
        self.user = user.strip('\@')
        self.fullname = fullname
        self.id = id
        self.url = url
        self.timestamp = timestamp
        self.text = text
        self.replies = replies
        self.retweets = retweets
        self.likes = likes
        self.html = html
        self.reply_to_id = reply_to_id if reply_to_id != id else '0'

    @classmethod
    def from_soup(cls, tweet):
        try:
            url = tweet.find('div', 'tweet')['data-permalink-path'] or ""
        except:
            url = None
        
        try:
            reply_to_id=tweet.find('div', 'tweet')['data-conversation-id'] or '0'
        except:
            reply_to_id = None

        return cls(
            user=tweet.find('span', 'username').text or "",
            fullname=tweet.find('strong', 'fullname').text or "", 
            id=tweet['data-item-id'] or "",
            url = url,
            timestamp=datetime.utcfromtimestamp(
                int(tweet.find('span', '_timestamp')['data-time'])),
            text=tweet.find('p', 'tweet-text').text or "",
            replies=tweet.find(
                'span', 'ProfileTweet-action--reply u-hiddenVisually').find(
                    'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0',
            retweets=tweet.find(
                'span', 'ProfileTweet-action--retweet u-hiddenVisually').find(
                    'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0',
            likes=tweet.find(
                'span', 'ProfileTweet-action--favorite u-hiddenVisually').find(
                    'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0',
            html=str(tweet.find('p', 'tweet-text')) or "",
            reply_to_id=reply_to_id
        )


    @classmethod
    def from_html(cls, html):
        soup = BeautifulSoup(html, "lxml")
        tweets = soup.find_all('li', 'js-stream-item')
        if tweets:
            for tweet in tweets:
                try:
                    yield cls.from_soup(tweet)
                except AttributeError:
                    pass  # Incomplete info? Discard!
