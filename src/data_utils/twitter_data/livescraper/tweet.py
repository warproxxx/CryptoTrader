from coala_utils.decorators import generate_ordering
import time

@generate_ordering('timestamp', 'id', 'text', 'user', 'replies', 'retweets', 'likes', 'reply_to_id', 'response_type')
class Tweet:
    def __init__(self, user, id, timestamp, text, replies, retweets, likes, reply_to_id, response_type):
        self.user = user
        self.id = id
        self.timestamp = timestamp
        self.text = text
        self.replies = replies
        self.retweets = retweets
        self.likes = likes
        self.reply_to_id = reply_to_id if reply_to_id != id else '0'
        self.response_type = response_type
    
    @classmethod
    def from_tweepy(cls, tweet):
        response_type = 'tweet'
        in_response_to = tweet.in_reply_to_status_id
        
        if in_response_to == None:
            if hasattr(tweet, 'retweeted_status'):
                response_type = 'retweet'
                in_response_to = tweet.retweeted_status.id
            else:
                if hasattr(tweet, 'quoted_status'):
                    response_type = 'quoted_retweet'
                    in_response_to = tweet.quoted_status.id
                else:
                    in_response_to = '0'
        else:
            response_type = 'reply'
            
        tweetText = ''
        try:
            tweetText = tweetText + tweet.extended_tweet['full_text']
        except:
            try:
                tweetText = tweetText + tweet.text
            except:
                pass

        try:
            tweetText = tweetText + ' <retweeted_status> ' + tweet.retweeted_status.extended_tweet['full_text'] + ' </retweeted_status>'
        except:
            try:
                tweetText = tweetText + ' <retweeted_status> ' + tweet.retweeted_status.text + ' </retweeted_status>'
            except:
                pass

        try:
            tweetText = tweetText + ' <quoted_status> ' + tweet.quoted_status.extended_tweet['full_text'] + ' </quoted_status>'
        except:
            try:
                tweetText = tweetText + ' <quoted_status> ' + tweet.quoted_status.text + ' </quoted_status>'
            except:
                pass
            
            
        if 'urls' in tweet.entities:
            for url in tweet.entities['urls']:
                try:
                    tweetText = tweetText.replace(url['url'], url['expanded_url'])
                except:
                    pass
        
        timeInt = 0
        
        
        try:
            timeInt = int(time.mktime(tweet.created_at.timetuple()))
        except:
            pass

        return cls(
            user=tweet.user.screen_name,
            id=tweet.id,
            timestamp=timeInt,
            text=tweetText,
            replies=0,
            retweets=tweet.retweet_count,
            likes=tweet.favorite_count,
            reply_to_id=in_response_to,
            response_type=response_type
        )