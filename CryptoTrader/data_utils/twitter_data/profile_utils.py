from profilescraper import query_profile
import pandas as pd
import itertools

import os

from glob import glob

import numpy as np

from proxy_utils import proxy_dict, get_proxies

from datetime import datetime, timedelta

import numba

class profileDownloader:
    def __init__(self, logger=None):
        
        if logger == None:
            logger = logging.getLogger()
            logger.basicConfig = logging.basicConfig(filename=__file__.replace('profile_utils.py', 'logs/profile_logs.txt'),level=logging.INFO)
            
        self.logger=logger
        self.currpath = __file__.replace('/profile_utils.py', '')
        
        
    def profiles_to_pandas(self, profiles):
        userDf = pd.DataFrame(columns=['username', 'location', 'has_location', 'created', 'is_verified', 'total_tweets', 'total_following', 'total_followers', 'total_likes', 'total_moments', 'total_lists', 'has_avatar', 'has_background', 'is_protected', 'profile_modified', 'tweets'])
        tweetDf = pd.DataFrame(columns=['User', 'ID', 'Tweet', 'Time', 'Likes', 'Replies', 'Retweet'])

        for profile in profiles:   
            for tweet in profile.tweets:
                tweetDf = tweetDf.append({'User': profile.username, 'ID': tweet.id, 'Tweet': tweet.text, 'Time': tweet.timestamp, 'Likes': tweet.likes, 'Replies': tweet.replies, 'Retweet': tweet.retweets}, ignore_index=True)

            userDf = userDf.append({'username':profile.username, 'location':profile.location, 'has_location':profile.has_location, 'created':profile.created, 'is_verified':profile.is_verified, 'total_tweets':profile.total_tweets, 'total_following':profile.total_following, 'total_followers':profile.total_followers, 'total_likes':profile.total_likes, 'total_moments':profile.total_moments, 'total_lists':profile.total_lists, 'has_avatar':profile.has_avatar, 'has_background':profile.has_background, 'is_protected':profile.is_protected, 'profile_modified':profile.profile_modified}, ignore_index=True)

        tweetDf = tweetDf.to_csv(self.currpath + '/data/profiledata/userTweets.csv', index=None, mode='a')
        userDf['username'].to_csv(self.currpath + '/data/profiledata/extractedUsers.csv', index=None, mode='a')
        userDf.to_csv(self.currpath + '/data/profiledata/userData.csv', index=None, mode='a')

        self.logger.info("Saved to userTweets.csv and extractedUsers.csv")
        
    def scrape_list(self, currList, poolsize, proxy, count):
        if (len(currList) > 0):
            profiles = query_profile(currList, poolsize=poolsize, proxy=proxy)
            self.profiles_to_pandas(profiles)

            count += 1

        return count
    
    def extract(self, coinname, poolsize=20):
        proxies = get_proxies()
        proxySize = len(proxies)

        users = list(set(pd.read_csv(self.currpath + '/data/{}/extracted/combined.csv'.format(coinname), dtype=str)['User']))

        try:
            alreadyRead = pd.read_csv(self.currpath + '/data/profiledata/extractedUsers.csv', header=None)[0]
        except FileNotFoundError:
            self.logger.info("Already extracted users not found - Starting from a clean slate")
            os.mknod(self.currpath + "/data/profiledata/extractedUsers.csv")
            alreadyRead = pd.Series()


        uniqueUsers = list(set(users) - set(alreadyRead))

        self.logger.info("File contains {} data. Scraping for {} after cache".format(len(users), len(uniqueUsers)))

        oldi = 0
        count = 0

        for i in range(0, len(uniqueUsers), poolsize*5):
            count = self.scrape_list(uniqueUsers[oldi:i], poolsize=poolsize, proxy=proxies[count], count=count)

            if (count >= proxySize):
                count = 0

            self.logger.info("Done {} of {}".format(i, len(uniqueUsers)))
            oldi = i

        scrape_list(uniqueUsers[i:], poolsize=poolsize, proxy=None, count=count)
    
    def perform_scraping(self, poolsize=30):
        for files in glob(self.currpath + "/data/*"):
            if (os.path.exists(files + "/extracted")):
                self.logger.info("Extracting for {}".format(files))
                self.extract(files.split("/")[-1], poolsize=poolsize)
                
class profileUtils:
    def __init__(self):
        self.currpath = __file__.replace('/profile_utils.py', '')
    
    def print_details(self):
        allUsers = pd.DataFrame()

        for files in glob(self.currpath + "/data/*"):
            if (os.path.exists(files + "/extracted")):
                fname = files + "/extracted/combined.csv"
                tDf = pd.read_csv(fname)
                print("Reading from {}".format(fname))
                allUsers = pd.concat([allUsers, tDf['User']]) 
                
    @numba.jit
    def clean_files(self):
        userData = pd.read_csv(self.currpath + "/data/profiledata/userData.csv", low_memory=False)
        userTweets = pd.read_csv(self.currpath + "/data/profiledata/userTweets.csv", low_memory=False)

        userTweets = userTweets.rename(columns={'User': 'username'})

        merged = pd.merge(userData, userTweets, how='inner', on=['username'])    
        newuserData = merged[userData.columns]
        newuserData = newuserData.set_index('username').drop_duplicates().reset_index()

        newuserTweets = merged[userTweets.columns]
        newuserTweets = newuserTweets.rename(columns={'username': 'User'})

        newuserTweets = newuserTweets.set_index(['User', 'ID']).drop_duplicates().reset_index()

        newuserData.to_csv(self.currpath + "/data/profiledata/userData.csv", index=None)
        newuserTweets.to_csv(self.currpath + "/data/profiledata/userTweets.csv", index=None)
        newuserData['username'].to_csv(self.currpath + "/data/profiledata/extractedUsers.csv", index=None)
        
    def age_to_created():
        userData = pd.read_csv(self.currpath  + '/data/profiledata/userData.csv')
        userData['age'] = pd.to_numeric(userData['age'], errors='coerce').fillna(0).astype(int)

        userData.insert(1, 'created', 0)
        userData['created'] = userData['age'].apply(lambda x: (datetime.now() - timedelta(days=int(x))).strftime("%Y-%m-%d"))
        userData = userData.drop('age', axis=1)
        userData = userData.drop('tweets', axis=1)
        return userData