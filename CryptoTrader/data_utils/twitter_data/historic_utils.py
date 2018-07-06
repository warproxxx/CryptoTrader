from twitterscraper import query_tweets

from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY
from datetime import datetime, date, timedelta

from proxy_utils import proxy_dict, get_proxies

import pandas as pd
import time

import os

import numpy as np

import requests

from glob import glob

import logging


class historicDownloader:
    def __init__(self, detailsList, logger=None):
        '''
        Parameters:
        ___________
        
        detailsList (list): 
        List containing keyword, coinname in string and start and end in date format
        
        logger (logger):
        Saves to file if not provided else default
        '''
        
        if logger == None:
            logger = logging.getLogger()
            logger.basicConfig = logging.basicConfig(filename=__file__.replace('historic_utils.py', 'logs/historic_logs.txt'),level=logging.INFO)
            
        self.logger = logger
        
        self.detailsList = detailsList
        self.currpath = __file__.replace('/historic_utils.py', '')
        
    def scrape(self, start_date, end_date, form, proxy, keyword, coinname):                                         
        delta = relativedelta(months=1)
        dic = {}

        while start_date <= end_date:
            temp_start=start_date

            start_date += delta

            temp_end = start_date

            if start_date > end_date:
                temp_end = end_date
            
            fname = "data/tweet/{}/historic_scrape/raw/{}_{}.csv".format(coinname.lower(), temp_start.strftime('%Y-%m-%d'), temp_end.strftime('%Y-%m-%d'))
            final_directory = os.path.join(self.currpath, fname)     

            #do if file dosen't exisst
            if not os.path.exists(final_directory):
                df = pd.DataFrame(columns=['ID', 'Tweet', 'Time', 'User', 'Likes', 'Replies', 'Retweet', 'in_response_to', 'response_type'])

                self.logger.info("Current Starting Date:{} Current Ending Date:{}".format(temp_start, temp_end))
                selectedDays = (temp_end - temp_start).days
                
                list_of_tweets = []
                list_of_tweets = query_tweets(keyword, 10000 * selectedDays, begindate=temp_start, enddate=temp_end, poolsize=selectedDays, proxies=proxy)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
                        
                for tweet in list_of_tweets:
                    res_type = tweet.response_type

                    if (tweet.reply_to_id == '0'):
                        res_type='tweet'

                    df = df.append({'ID': tweet.id, 'Tweet': tweet.text, 'Time': tweet.timestamp, 'User': tweet.user, 'Likes': tweet.likes, 'Replies': tweet.replies, 'Retweet': tweet.retweets, 'in_response_to': tweet.reply_to_id, 'response_type': tweet.response_type}, ignore_index=True)
                
                if form == "save":
                    df.to_csv(fname, index=False)
                else:
                    dic[temp_start.strftime("%Y-%m-%d")] = df

        if form == "return":
            return dic
                
                
    def perform_scraping(self, form = "save"):
        '''
        Parameters:
        ___________
     
        form (string):
        If set to save, the data will be saved to pandas dataframe.
        If set to return, the data will be returned as dictionary
        '''
        
        proxies = get_proxies()
        proxySize = len(proxies)
        
        all_data = {}        
        count = 0

        for coinDetail in self.detailsList:
            self.logger.info("Scraping {} Data".format(coinDetail['coinname']))
            self.logger.info("Starting Year: {} Ending Year: {}".format(coinDetail['start'].year, coinDetail['end'].year))

            proxy = proxies[count]
            
            start_date = coinDetail['start']
            end_date = coinDetail['end']
            
            delta = relativedelta(years=1)
            tData = {}
            
            while start_date <= end_date:
                temp_start=start_date

                start_date += delta

                temp_end = start_date

                if start_date > end_date:
                    temp_end = end_date
                
                if form == "save":
                    self.scrape(temp_start, temp_end, form, proxy=proxy, keyword=coinDetail['keyword'], coinname=coinDetail['coinname'])
                elif form == "return":
                    tData.update(self.scrape(temp_start, temp_end, form, proxy=proxy, keyword=coinDetail['keyword'], coinname=coinDetail['coinname']))
                    
                count +=1

                if (count >= proxySize):
                    count = 0
            
            all_data[coinDetail['coinname']] = tData
            
        if form == "return":
            return all_data
                    
class historicUtils:
    def __init__(self, detailsList, logger=None):
        
        if logger == None:
            logger = logging.getLogger()
            logger.basicConfig = logging.basicConfig(filename=__file__.replace('historic_utils.py', 'logs/historic_logs.txt'),level=logging.INFO)
            
        self.logger = logger
        
        self.detailsList = detailsList
        self.currpath = __file__.replace('/historic_utils.py', '')
        
        self.rawpaths = []
        
        self.coinKeywords = {}
        
        for coin in self.detailsList:
            self.rawpaths.append(self.currpath + "/tweet/{}/historic_scrape/raw".format(coin['coinname']))
            self.coinKeywords[coin['coinname']] = coin['keyword']
                 
                
    def deleteFiles(self):
        '''
        Deletes the extracted data for given coins
        '''
        for path in self.rawpaths:
            
            for f in glob(path + "/*"):
                self.logger.info("Deleting {}".format(f))
                os.remove(f)
                
    def merge_data(self):
        '''
        Merges the data across different files and converts it into combined.csv
        '''

        for path in self.rawpaths:
            fullDf = pd.DataFrame(columns=['ID', 'Tweet', 'Time', 'User', 'Likes', 'Replies', 'Retweet', 'in_response_to', 'response_type'])

            writeFile = fullPath + "/" + "combined.csv"

            if (os.path.isfile(writeFile)):
                os.remove(writeFile)

            for file in os.listdir(path):
                csv = fullPath + "/" + file

                if (".csv" in csv):
                    df = pd.read_csv(csv, engine='python')
                    fullDf = pd.concat([fullDf, df])
                    logging.info("Concating {}".format(csv))

            fullDf = self.clean_data(fullDf)
            fullDf.to_csv(writeFile, index=False)
            
            
    def clean_data(self, fullDf):
        fullDf = fullDf.reset_index(drop=True)
        fullDf = fullDf.replace(np.inf, np.nan)
        fullDf = fullDf.fillna(method='ffill')

        fullDf['Time'] = pd.to_datetime(fullDf['Time'], errors='coerce')
        fullDf = fullDf.dropna(subset=['Time'])
        fullDf = fullDf.sort_values(by='Time')
        fullDf = fullDf.drop_duplicates()

        return fullDf
    
    def get_missing_days(self, df, freq=24):
        df['Time'] = pd.to_datetime(df['Time'])

        new = pd.DataFrame(columns=['Time', 'Frequency'])

        new['Time'] = df['Time']
        new['Frequency'] = 1

        new.set_index('Time', inplace = True)
        per_24 = new['Frequency'].resample('{}H'.format(freq)).sum().fillna(0)
        miss_dates = per_24[per_24 == 0].index
        return miss_dates
    
    def fill_missing_days(self):
        newDetail = []
        
        for fullPath in self.rawpaths:
            coinName = fullPath.split("/")[-3]
            
            df = pd.read_csv('{}/combined.csv'.format(fullPath))
            miss_dates = self.get_missing_days(df)

            tweetDf = pd.DataFrame(columns=['ID', 'Tweet', 'Time', 'User', 'Likes', 'Replies', 'Retweet', 'in_response_to', 'response_type'])

            for dates in miss_dates:
                date_from = dates - pd.DateOffset(days=2)
                date_to = dates + pd.DateOffset(days=2)
            
                newDetail.append({'coinname': coinName, 'start': date_from, 'end': date_to})
        
        #merging same dates dosen't seem necessary. But this can be optimized that way
        
        for i, detail in enumerate(newDetails):
            tDic = newDetail[i]
            tDic['keyword'] = self.coinKeywords[detail['coinname']]
            newDetail[i] = tDic
        
        hu = historicDownloader()
        hu.perform_scraping()