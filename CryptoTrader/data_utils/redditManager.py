import pandas as pd
import sqlite3
from num2words import num2words
import os

from datetime import date, timedelta
import datetime
import time

import data_utils

import subprocess
import sys

import numpy as np

import re

class redditManager():

    def __init__(self, subreddits = ['altcoin', 'Bitcoin', 'Bitcoincash', 'BitcoinMarkets', 'btc', 'cryptocurrency', 'CryptoMarkets', 'dashpay', 'dogecoin', 'ethereum', 'ethtrader', 'litecoin', 'Monero', 'Ripple', 'Stellar', 'xmrtrader']):
        '''
        coins (dictionary): Dictionary containing name of coins
        '''
        self.subreddits = subreddits
        self.directory = os.path.dirname(data_utils.__file__)

    def downloader(self):
        
        fname = self.directory + "\\reddit_data\\timesearch-master\\timesearch.py"
        

        for subreddit in self.subreddits:
            command = "python \"{}\" timesearch -r {}".format(fname, subreddit)
            print(command)

            process = subprocess.Popen(command, stdout=subprocess.PIPE)

            for line in process.stdout:
                sys.stdout.write(line)

    def sql_to_pandas(self, coinname):
        con = sqlite3.connect(self.directory + "\\reddit_data\\timesearch-master\\subreddits\\{}\\{}.db".format(coinname, coinname))
        df = pd.read_sql_query("SELECT * FROM submissions", con)
        
        df = df[['created', 'author', 'title', 'url', 'score', 'num_comments', 'flair_text', 'selftext']]

        df.to_csv('a.csv')
        return df

    def merge_data(self, coinname, df, cachetime):
        fName = self.directory + "\\reddit_data\\readable\\{}-{}.csv".format(coinname, cachetime)
    
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

                #cols = 'title ' + valsBetween['title'] + ' score ' + valsBetween['score'].apply(lambda x: num2words(x)) + ' comments ' + valsBetween['num_comments'].apply(lambda x: num2words(x))
                cols = 'title ' + valsBetween['title'] + ' score ' + valsBetween['score'].map(str) + ' comments ' + valsBetween['num_comments'].map(str)
                new['Reddit'][i] = (cols.str.cat(sep='\n'))
                oldDate = new['Date'][i]
            
            new.to_csv(fName)
        
        return new

    #gensim and all