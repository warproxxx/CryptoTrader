from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream, API
from libs.reading_utils import get_twitter

from dateutil.parser import parse
import time

from livescraper.profile import Profile
from livescraper.tweet import Tweet

class TestTweet_Profile:
    def setup_method(self):
        consumer_key, consumer_secret, access_token, access_token_secret = get_twitter()

        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        self.api = API(auth)

        query = "Bitcoin"
        
        self.results = self.api.search(q=query, count=10)

    def test_tweet(self):
        tweet = Tweet.from_tweepy(self.results[0])
        assert(len(tweet.user.split()) == 1)
        assert(int(tweet.id) > 10000)
        assert((time.time() - int(tweet.timestamp)) <=  20) #some better test here
        assert(tweet.text)
        assert(int(tweet.replies) >= 0)
        assert(int(tweet.retweets) >= 0)
        assert(int(tweet.likes) >= 0)
        assert(int(tweet.reply_to_id) >= 0)
        assert(any(x in tweet.response_type for x in ['tweet', 'retweet', 'quoted_status', 'quoted_retweet', 'reply']))

    def test_profile(self):
        profile = Profile.from_profile(self.results[0])

        assert(len(profile.username.split()) == 1)
        print(profile.location)
        assert(profile.has_location in [0, 1]) 
        assert(parse(profile.created))
        
        assert(profile.is_verified in [0,1])
        assert(int(profile.total_tweets) >= 0)
        assert(int(profile.total_following) >= 0)
        assert(int(profile.total_followers) >= 0)
        assert(int(profile.total_likes) >= 0)
        assert(profile.has_avatar in [0,1])
        assert(profile.has_background in [0,1])
        assert(profile.is_protected in [0,1])
        assert(profile.profile_modified in [0,1])