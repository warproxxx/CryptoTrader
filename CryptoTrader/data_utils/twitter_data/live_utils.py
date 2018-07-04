from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream, API
import time
import json
import pandas as pd
import numpy as np
import logging
import threading
import time

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

        self.df = self.df.append(pd.Series({'ID': tweet.id, 'Tweet': tweetText, 'Time': tweet.created_at, 'User': tweet.user.screen_name, 'Likes': tweet.favorite_count, 'Replies': 0, 'Retweets': tweet.retweet_count, 'in_response_to': in_response_to, 'response_type': response_type, 'coinname': self.find_key(tweetText, self.keywords)}), ignore_index=True)
        has_avatar = 0 if 'default_profile_images' in tweet.user.profile_image_url else 1
        has_background = int(tweet.user.profile_use_background_image)
        has_location = int(tweet.user.geo_enabled)
        if has_location == 1:
            location = tweet.user.location
        else:
            location = 0
            
        profile_modified = 1 if has_background == 1 or has_avatar == 1 or has_location != 0 else 0
        self.userData = self.userData.append(pd.Series({'username': tweet.user.screen_name, 'location': location, 'has_location': has_location, 'created': tweet.user.created_at.strftime('%Y-%m-%d'), 'is_verified': int(tweet.user.verified), 'total_tweets': tweet.user.statuses_count, 'total_following': tweet.user.friends_count, 'total_followers': tweet.user.followers_count, 'total_likes': tweet.user.favourites_count, 'has_avatar': has_avatar, 'has_background': has_background, 'is_protected': int(tweet.user.protected), 'profile_modified': profile_modified}), ignore_index=True)
        
        if self.df.shape[0] > 1000:
            self.end_time = int(time.time())  
            t1 = threading.Thread(target=liveDownloader.save_data, args=[self.logger, self.df, self.userData, self.start_time, self.end_time])
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
            logfile=__file__.replace('live_utils.py', 'logs/live.txt')
            logger.basicConfig = logging.basicConfig(filename=logfile, level=logging.INFO)
            
        self.logger = logger
        
        
        self.keywords = keywords
        self.keywordsOnly = [value for key, values in keywords.items() for value in values]
        
    def save_data(logger, df, userData, start_time, end_time):
        fname = "{}_{}".format(start_time, end_time)
        currpath = __file__.replace("live_utils.py", "")
        
        df.to_csv(currpath + "data/live/{}.csv".format(fname), index=False)
        logger.info("Saved to live/{}.csv in a new thread".format(fname))
                
        userData.to_csv(currpath + "data/profiledata/live/{}.csv".format(fname), index=False)
        logger.info("Saved to profiledata/live/{}.csv in a new thread".format(fname))

    def get_listener(self, access_token='852009551876431872-OfvYX17eqrPz9eERGaRVxKfkBPVALyO', access_token_secret='koQa3hgW22EsgdvseQVsj3KnYbzHc564xEVfr7lYiPGhy', consumer_key='95fyXonGGIHKgfothfbOOAM7p', consumer_secret='6KWDuC87go4CbFE6jLdRnHWGFcj2Fl9hQvdizfaiwCOdZliv49'):
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        listener = MyStreamListener(self.logger, self.keywords)
        return listener, auth

    def collect(self):
        listener, auth = self.get_listener()
        myStream = Stream(auth=auth, listener=listener)
        
        self.logger.info("Started collecting data for {}".format(self.keywordsOnly))
        while True:
            try:
                myStream.filter(track=self.keywordsOnly, languages=['en'])
            except KeyboardInterrupt:
                df, userData, start_time = listener.get_data()     
                self.logger.info("Keyboard interrupted. Saving whatever has been collected")
                
                t1 = threading.Thread(target=liveDownloader.save_data, args=[self.logger, df, userData, start_time, int(time.time())])
                t1.start()
                
                return df, userData

            except Exception as e:
                self.logger.warning(('Got an exception. Error is: {}. Saving whatever exists').format(str(e)))
                df, userData, start_time = listener.get_data()                                
                
                end_time = int(time.time())
                
                t1 = threading.Thread(target=liveDownloader.save_data, args=[self.logger, df, userData, start_time, end_time])
                t1.start()                
               
                listener, auth = self.get_listener()
                myStream = Stream(auth=auth, listener=listener)