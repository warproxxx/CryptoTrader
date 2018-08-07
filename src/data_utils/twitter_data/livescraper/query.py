from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream, API

from livescraper.profile import Profile
from livescraper.tweet import Tweet

from libs.writing_utils import get_locations, get_logger
from libs.reading_utils import get_twitter
from libs.run_utils import runUtils

import threading

import pandas as pd
import json
import time

class MyStreamListener(StreamListener):

    def __init__(self, keywords, logger=None, tweetCount=0):
        '''
        Parameters:
        ___________
        keywords: (dict)
        Dictionary containing coinname and its relevant keywords
        Example:
        {'bitcoin': ['bitcoin', 'BTC'], 'dashcoin': ['dashcoin', 'DASH', 'darkcoin']}

        tweetCount (int) (optional):
        If not set to 0, the program will terminate after n tweets is found
        '''

        _, self.currRoot_dir = get_locations()

        if (logger == None):
            self.logger = get_logger(self.currRoot_dir + '/logs/live.txt')
        else:
            self.logger = logger

        self.api = API()
        self.df = pd.DataFrame(columns=['ID', 'Tweet', 'Time', 'User', 'Likes', 'Replies', 'Retweets', 'in_response_to', 'response_type', 'coinname'])
        self.userData = pd.DataFrame(columns=['username', 'created', 'location', 'has_location', 'is_verified', 'total_tweets', 'total_following', 'total_followers', 'total_likes', 'has_avatar', 'has_background', 'is_protected', 'profile_modified'])
        self.keywords = keywords
        self.start_time = int(time.time())
        self.tweetCount = tweetCount
        self.statusCount = 0

    def on_status(self, tweet):
        tweetData = Tweet.from_tweepy(tweet)
        profileData = Profile.from_profile(tweet)
        
        self.df = self.df.append(pd.Series({'ID': tweetData.id, 'Tweet': tweetData.text, 'Time': tweetData.timestamp, 'User': tweetData.user, 'Likes': tweetData.likes, 'Replies': 0, 'Retweets': tweetData.replies, 'in_response_to': tweetData.reply_to_id, 'response_type': tweetData.response_type, 'coinname': self.find_key(tweetData.text, self.keywords)}), ignore_index=True)
        self.userData = self.userData.append(pd.Series({'username': profileData.username, 'location': profileData.location, 'has_location': profileData.has_location, 'created': profileData.created, 'is_verified': profileData.is_verified, 'total_tweets': profileData.total_tweets, 'total_following': profileData.total_following, 'total_followers': profileData.total_followers, 'total_likes': profileData.total_likes, 'has_avatar': profileData.has_avatar, 'has_background': profileData.has_background, 'is_protected': profileData.is_protected, 'profile_modified': profileData.profile_modified}), ignore_index=True)

        self.statusCount = self.statusCount + 1

        if (self.tweetCount != 0):
            if self.statusCount >= self.tweetCount:
                return False

        if (self.df.shape[0] % 100 == 0):
            self.logger.info("Collected 100 data")

        if (self.df.shape[0] > 1000):
            self.end_time = int(time.time())  
            t1 = threading.Thread(target=query_live_tweets(self.keywords).save_data, args=[self.df, self.userData, self.start_time, self.end_time])
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
        '''
        Returns:
        ________
        df (Pandas Dataframe):
        Dataframe containing Tweet Information

        userData (Pandas Dataframe):
        Dataframe containing Profile Information

        start_time (int):
        int timestamp of when the scraping was started for the current batch
        '''
        
        return self.df, self.userData, self.start_time

    def on_error(self, status_code):
        if status_code == 420:
            self.logger.warning('420 Error')
            return False


class query_live_tweets():
    def __init__(self, keywords, logger=None, tweetCount=0):
        """
        Parameters:
        ___________
        keywords (dictionary):
        Dictionary containing coinname and its relevant keywords
        Example:
        {'bitcoin': ['bitcoin', 'BTC'], 'dashcoin': ['dashcoin', 'DASH', 'darkcoin']}

        tweetCount (int) (optional):
        If not set to 0, the program will terminate after n tweets is found
        """

        _, self.currRoot_dir = get_locations()
        self.tweetCount = tweetCount

        self.keywords = keywords
        self.coins = [key for key, value in keywords.items()]
        self.keywordsOnly = [value for key, values in keywords.items() for value in values]

        if (logger == None):
            self.logger = get_logger(self.currRoot_dir + '/logs/live.log')
        else:
            self.logger = logger

        runUtils(self.keywords).create_directory_structure()
        

    def get_listener(self, create=True, apiFile="/data/static/api.json"):

        if create == True:
            consumer_key, consumer_secret, access_token, access_token_secret = get_twitter(apiFile)

            auth = OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            listener = MyStreamListener(self.keywords, self.logger, self.tweetCount)
            self.listener = listener
            self.auth = auth
            return self.listener, self.auth
        else:
            return self.listener, self.auth


    def perform_search(self):
        myStream = Stream(auth=self.auth, listener=self.listener)
        myStream.filter(track=self.keywordsOnly, languages=['en'])

    def get_stream(self):
        listener,auth = self.get_listener()
        myStream = Stream(auth=auth, listener=listener)

        self.logger.info("Started collecting data for {}".format(self.keywordsOnly))

        return self.logger, self.keywordsOnly, listener, myStream

    def save_data(self, df, userData, start_time, end_time, relative_dir="/"):
        '''
        Parameters:
        ___________
        df (Dataframe):
        Pandas Dataframe containing tweets

        userData (Dataframe):
        Pandas Dataframe containing profile information

        start_time (int):
        timestamp so as to include in file name

        end_time (int):
        timestamp so as to include in file name

        relative_dir (string) (optional):
        The directory inside to save
        '''
        #run the folder structure creator from run_utils before this
        fname = "{}_{}".format(start_time, end_time)

        for coinname in self.coins:
            tDf = df[df['coinname'] == coinname].drop('coinname', axis=1)
            tDf.to_csv(self.currRoot_dir + relative_dir +"data/tweet/{}/live/{}.csv".format(coinname, fname), index=False)
            self.logger.info("Saved to {}data/tweet/{}/live/{}.csv in a new thread".format(relative_dir, coinname, fname))
            
        userData.to_csv(self.currRoot_dir + relative_dir + "data/profile/live/{}.csv".format(fname), index=False)
        self.logger.info("Saved to {}data/profile/live/{}.csv in a new thread".format(relative_dir, fname))