from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream, API
from livescraper import Profile, Tweet

import threading

import logging

import pandas as pd
import time

logger = logging.getLogger()
masterPath = __file__.replace('liverscraper/query.py', '')
logfile = masterPath + ('logs/live.txt')
logger.basicConfig = logging.basicConfig(filename=logfile, level=logging.INFO)

def save_data(df, userData, start_time, end_time, coins):
    fname = "{}_{}".format(start_time, end_time)
    
    for coinname in coins:
        tDf = df[df['coinname'] == coinname].drop('coinname', axis=1)
        tDf.to_csv(masterPath + "/data/tweet/{}/live/{}.csv".format(coinname, fname), index=False)
        logger.info("Saved to /data/tweet/{}/live/{}.csv in a new thread".format(coinname, fname))
        
    userData.to_csv(masterPath + "/data/profile/live/{}.csv".format(fname), index=False)
    logger.info("Saved to data/profile/live/{}.csv in a new thread".format(fname))

class MyStreamListener(StreamListener):

    def __init__(self, logger, keywords):
        self.logger = logger
        self.api = API()
        self.df = pd.DataFrame(columns=['ID', 'Tweet', 'Time', 'User', 'Likes', 'Replies', 'Retweets', 'in_response_to', 'response_type', 'coinname'])
        self.userData = pd.DataFrame(columns=['username', 'created', 'location', 'has_location', 'is_verified', 'total_tweets', 'total_following', 'total_followers', 'total_likes', 'has_avatar', 'has_background', 'is_protected', 'profile_modified'])
        self.keywords = keywords
        self.start_time = int(time.time())
        self.currpath = __file__.replace("live_utils.py", "")

    def on_status(self, tweet):
        tweetData = Tweet.from_tweepy(tweet)
        profileData = Profile.from_profile(tweet)
        
        self.df = self.df.append(pd.Series({'ID': tweetData.id, 'Tweet': tweetData.text, 'Time': tweetData.timestamp, 'User': tweetData.user, 'Likes': tweetData.likes, 'Replies': 0, 'Retweets': tweetData.replies, 'in_response_to': tweetData.in_response_to, 'response_type': tweetData.response_type, 'coinname': self.find_key(tweetData.text, self.keywords)}), ignore_index=True)
        self.userData = self.userData.append(pd.Series({'username': profileData.username, 'location': profileData.location, 'has_location': profileData.has_location, 'created': profileData.created, 'is_verified': profileData.is_verified, 'total_tweets': profileData.total_tweets, 'total_following': profileData.total_following, 'total_followers': profileData.total_followers, 'total_likes': profileData.total_likes, 'has_avatar': profileData.has_avatar, 'has_background': profileData.has_background, 'is_protected': profileData.is_protected, 'profile_modified': profileData.profile_modified}), ignore_index=True)

        if (self.df.shape[0] > 1000):
            self.end_time = int(time.time())  
            t1 = threading.Thread(target=save_data, args=[self.logger, self.df, self.userData, self.start_time, self.end_time])
            t1.start()
            self.df, self.userData = self.df[:0], self.userData[:0]
            self.start_time = self.end_time

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
        return self.df, self.userData, self.start_time

    def on_error(self, status_code):
        if status_code == 420:
            self.logger.warning('420 Error')
            return False


def get_listener(keywords, access_token='852009551876431872-OfvYX17eqrPz9eERGaRVxKfkBPVALyO', access_token_secret='koQa3hgW22EsgdvseQVsj3KnYbzHc564xEVfr7lYiPGhy', consumer_key='95fyXonGGIHKgfothfbOOAM7p', consumer_secret='6KWDuC87go4CbFE6jLdRnHWGFcj2Fl9hQvdizfaiwCOdZliv49'):
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    listener = MyStreamListener(logger, keywords)
    return listener, auth

def query_tweets(keywords):
    """
    Parameters:
    ___________
    keywords (dictionary):
    Dictionary containing coinname and its relevant keywords
    Example:
    {'bitcoin': ['bitcoin', 'BTC'], 'dashcoin': ['dashcoin', 'DASH', 'darkcoin']}
    """
    coins = [key for key, value in keywords.items()]
    keywordsOnly = [value for key, values in keywords.items() for value in values]
    
    listener,auth = get_listener(keywords)
    myStream = Stream(auth=auth, listener=listener)

    logger.info("Started collecting data for {}".format(keywordsOnly))

    return logger, keywordsOnly, listener, myStream

    while True:
        try:
            myStream.filter(track=keywordsOnly, languages=['en'])
        except KeyboardInterrupt:
            df, userData, start_time = listener.get_data()     
            logger.info("Keyboard interrupted. Saving whatever has been collected")
            
            t1 = threading.Thread(target=save_data, args=[df, userData, start_time, int(time.time()), coins])
            t1.start()
            
            return df, userData

        except Exception as e:
            logger.warning(('Got an exception. Error is: {}. Saving whatever exists').format(str(e)))
            df, userData, start_time = listener.get_data()                                
            
            end_time = int(time.time())
            
            t1 = threading.Thread(target=save_data, args=[df, userData, start_time, end_time, coins])
            t1.start()                
            
            listener, auth = get_listener(keywords)
            myStream = Stream(auth=auth, listener=listener)