import pandas as pd
import sqlite3
from num2words import num2words
import os

from datetime import date, timedelta
import datetime
import time

import inspect

import subprocess
import sys

import numpy as np
import nltk

from multiprocessing.pool import Pool
import logging

from timesearch import timesearch

import re

class redditManager():

    def __init__(self):
        '''
        coins (dictionary): Dictionary containing name of coins
        '''
        self.directory = os.path.dirname(__file__)
        self.subreddits = os.listdir(self.directory + "/subreddits")
        
    def perform_download(self, subreddit, retries=10):
        try:
            logging.info("\nDownloading submissions from /r/{}".format(subreddit))
            timesearch.main(["timesearch", "-r", subreddit])
            logging.info("\nDownloading comments from /r/{}".format(subreddit))
            timesearch.main(["commentaugment", "-r", subreddit])
        except Exception as e:
            logging.info("Error: ".format(e.message))
            
        if retries > 0:
            return self.perform_download(subreddit, retries=retries-1)
        
        logging.error("Giving up")

    def downloader(self, subreddits="all"):
        '''
        Arguments:
        __________
        
        subreddits (string or list):
        If set to all, all subreddits are downloaded, else selected.
        
        Runs timesearchmaster to download data. 
        
        '''
        
        if type(subreddits) == str:
            subreddits = self.subreddits
            
        pools = Pool(len(subreddits))
        
        for _ in pools.imap_unordered(self.perform_download, self.subreddits):
            pass

    def sql_to_pandas(self, coinname):
        con = sqlite3.connect(self.directory + "/subreddits/{}//{}.db".format(coinname, coinname))
        df = pd.read_sql_query("SELECT * FROM submissions", con)
        
        df = df[['created', 'author', 'title', 'url', 'score', 'num_comments', 'flair_text', 'selftext']]

        df.to_csv('a.csv')
        return df

    def merge_data(self, coinname, df, cachetime):
        fName = self.directory + "/readable/{}-{}.csv".format(coinname, cachetime)
    
        if (os.path.isfile(fName)):
            new = pd.read_csv(fName)
        else:          
            reddit = self.sql_to_pandas(coinname)

            new = pd.DataFrame(columns=['Date', 'Reddit'])
            new['Date'] = df['Date']

            oldDate = new['Date'][0]

            for i in range(new.shape[0]):
                valsBetween = reddit[reddit['created'] > oldDate]
                valsBetween = valsBetween[reddit['created']  < new['Date'][i]]

                cols = 'title ' + valsBetween['title'] + ' score ' + valsBetween['score'].map(str) + ' comments ' + valsBetween['num_comments'].map(str)
                new['Reddit'][i] = (cols.str.cat(sep='\n'))
                oldDate = new['Date'][i]
            
            new.to_csv(fName)
        
        return new

    #gensim and all