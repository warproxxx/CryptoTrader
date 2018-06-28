from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream, API
import time, json, pandas as pd, logging

class MyStreamListener(StreamListener):

    def __init__(self, logger, keywords):
        self.logger = logger
        self.api = API()
        self.df = pd.DataFrame(columns=['ID', 'Tweet', 'Time', 'User', 'Likes', 'Replies', 'Retweets', 'in_response_to', 'response_type', 'coinname', 'debug'])
        self.userData = pd.DataFrame(columns=['username', 'created', 'location', 'has_location', 'is_verified', 'total_tweets', 'total_following', 'total_followers', 'total_likes', 'has_avatar', 'has_background', 'is_protected', 'profile_modified'])
        self.keywords = keywords

    def on_status(self, tweet):
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
            tweetText = tweetText + ' <retweeted_status> ' + tweet.retweeted_status.extended_tweet['full_text'] + '</retweeted_status>'
        except:
            try:
                tweetText = tweetText + ' <retweeted_status> ' + tweet.retweeted_status.text + '</retweeted_status>'
            except:
                pass

        try:
            tweetText = tweetText + ' <quoted_status> ' + tweet.quoted_status.extended_tweet['full_text'] + '</quoted_status>'
        except:
            try:
                tweetText = tweetText + ' <quoted_status> ' + tweet.quoted_status.text + '</quoted_status>'
            except:
                pass

        self.df = self.df.append(pd.Series({'ID': tweet.id, 'Tweet': tweetText, 'Time': tweet.created_at, 'User': tweet.user.screen_name, 'Likes': tweet.favorite_count, 'Replies': 0, 'Retweets': tweet.retweet_count, 'in_response_to': in_response_to, 'response_type': response_type, 'coinname': self.find_key(tweetText, self.keywords), 'debug': tweet}), ignore_index=True)
        has_avatar = 0 if 'default_profile_images' in tweet.user.profile_image_url else 1
        has_background = int(tweet.user.profile_use_background_image)
        has_location = int(tweet.user.geo_enabled)
        if has_location == 1:
            location = tweet.user.location
        else:
            location = 0
        profile_modified = 1 if has_background == 1 or has_avatar == 1 or has_location != 0 else 0
        self.userData = self.userData.append(pd.Series({'username': tweet.user.screen_name, 'location': location, 'has_location': has_location, 'created': tweet.user.created_at.strftime('%Y-%m-%d'), 'is_verified': int(tweet.user.verified), 'total_tweets': tweet.user.statuses_count, 'total_following': tweet.user.friends_count, 'total_followers': tweet.user.followers_count, 'total_likes': tweet.user.favourites_count, 'has_avatar': has_avatar, 'has_background': has_background, 'is_protected': int(tweet.user.protected), 'profile_modified': profile_modified}), ignore_index=True)
        return True

    def find_key(self, sentence, keywords):
        sentence = sentence.lower()
        for key, values in keywords.items():
            for value in values:
                if value.lower() in sentence:
                    return key

        return '0'

    def set_data(self, df, userData):
        self.df = df
        self.userData = userData

    def get_data(self):
        return (
         self.df, self.userData)

    def on_error(self, status_code):
        if status_code == 420:
            self.logger.warning('420 Error')
            return False


class liveDownloader:

    def __init__(self, keywords, logger=None):
        """
        Parameters:
        ___________
        keywords (dictionary):
        Dictionary containing coinname and its relevant keywords
        Example:
        {'bitcoin': ['bitcoin', 'BTC'], 'dashcoin': ['dashcoin', 'DASH', 'darkcoin']}
        """
        if logger == None:
            logger = logging.getLogger()
            logger.basicConfig = logging.basicConfig(filename=__file__.replace('live_utils.py', 'live_logs.txt'), level=logging.INFO)
        self.logger = logger
        self.keywords = keywords
        self.keywordsOnly = [value for value in keywords.items()]

    def get_listener(self, access_token='852009551876431872-OfvYX17eqrPz9eERGaRVxKfkBPVALyO', access_token_secret='koQa3hgW22EsgdvseQVsj3KnYbzHc564xEVfr7lYiPGhy', consumer_key='95fyXonGGIHKgfothfbOOAM7p', consumer_secret='6KWDuC87go4CbFE6jLdRnHWGFcj2Fl9hQvdizfaiwCOdZliv49'):
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        listener = MyStreamListener(self.logger, self.keywords)
        return (
         listener, auth)

    def collect(self):
        listener, auth = self.get_listener()
        myStream = Stream(auth=auth, listener=listener)
        while True:
            try:
                myStream.filter(track=self.keywordsOnly, languages=['en'])
            except KeyboardInterrupt:
                df, userData = listener.get_data()
                return (
                 df, userData)
            except Exception as e:
                self.logger.warning(('Got an exception. Error is: {}').format(str(e)))
                df, userData = listener.get_data()
                listener, auth = self.get_listener()
                listener.set_data(df, userData)
                myStream = Stream(auth=auth, listener=listener)