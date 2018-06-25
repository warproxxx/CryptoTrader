from datetime import datetime

from bs4 import BeautifulSoup
from coala_utils.decorators import generate_ordering


@generate_ordering('timestamp', 'id', 'text', 'user', 'replies', 'retweets', 'likes', 'reply_to_id', 'response_type')
class Tweet:
    def __init__(self, user, fullname, id, url, timestamp, text, replies, retweets, likes, html, reply_to_id, response_type):
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
        self.response_type = response_type
        
    @classmethod
    def from_soup(cls, tweet):        
        try:
            url = tweet.find('div', 'tweet')['data-permalink-path'] or ""
        except:
            url = None
                
        response_type = 'tweet'
        reply_to_id  = None
        
        try:
            reply_to_id=tweet.find('div', 'tweet')['data-conversation-id'] or '0'
            response_type = 'reply'
        except:
            reply_to_id = None
            
        try:
            reply_to_id=tweet.find('a', 'QuoteTweet-link')['data-conversation-id'] or '0'
            response_type='quoted_retweet'
        except:
            pass
                
        tweettext=""
        username=""
        fullname=""
        id=""
        timestamp=""
        
        try:
            tweettext=tweet.find('p', 'tweet-text').text or ""
        except:
            pass      
        
        try:
            tweettext = tweettext + " <quoted_status> " + tweet.find('div', 'QuoteTweet-text').text + "</quoted_status>"                           
        except:
            pass
        
        try:
            username=tweet.find('span', 'username').text or ""
        except:
            pass
        
        try:
            fullname=tweet.find('strong', 'fullname').text or ""
        except:
            pass
        
        try:
            id = tweet['data-item-id'] or ""
        except:
            pass
        
        try:
            timestamp=datetime.utcfromtimestamp(int(tweet.find('span', '_timestamp')['data-time']))
        except:
            pass
        
        replies='0'
        retweets='0'
        likes='0'
        html=""
        
        try:
            replies=tweet.find(
                    'span', 'ProfileTweet-action--reply u-hiddenVisually').find(
                        'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0'
        except:
            pass
        
        try:
            retweets=tweet.find(
                    'span', 'ProfileTweet-action--retweet u-hiddenVisually').find(
                        'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0'
        except:
            pass
        
      
        try:
            likes=tweet.find(
                    'span', 'ProfileTweet-action--favorite u-hiddenVisually').find(
                        'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0'
        except:
            pass
        
        
        try:
            html=str(tweet.find('p', 'tweet-text')) or ""
        except:
            pass
        
        
        return cls(
            user=username,
            fullname=fullname, 
            id=id,
            url=url,
            timestamp=timestamp,
            text=tweettext,
            replies=replies,
            retweets=retweets,
            likes=likes,
            html=html,
            reply_to_id=reply_to_id,
            response_type=response_type
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