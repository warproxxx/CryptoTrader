import pandas as pd
import numpy as np
import time

import os

from glob import glob

import logging

class basicUtils:
    def __init__(self, relativePath, coinnames):
        self.relativePath = relativePath
        self.coinnames = coinnames

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
            self.rawpaths.append(self.currpath + "/data/tweet/{}/historic_scrape/raw".format(coin['coinname']))
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

            writeFile = path + "/" + "combined.csv"

            if (os.path.isfile(writeFile)):
                os.remove(writeFile)

            for file in os.listdir(path):
                csv = path + "/" + file

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
        print(df)

        new = pd.DataFrame(columns=['Time', 'Frequency'])

        new['Time'] = df['Time']
        new['Frequency'] = 1

        new.set_index('Time', inplace = True)
        per_24 = new['Frequency'].resample('{}H'.format(freq)).sum().fillna(0)
        miss_dates = per_24[per_24 == 0].index
        return miss_dates
    
    def fill_missing_days(self):
        newDetails = []
        
        for fullPath in self.rawpaths:
            coinName = fullPath.split("/")[-3]
            
            df = pd.read_csv('{}/combined.csv'.format(fullPath))
            miss_dates = self.get_missing_days(df)
            print(miss_dates)

            tweetDf = pd.DataFrame(columns=['ID', 'Tweet', 'Time', 'User', 'Likes', 'Replies', 'Retweet', 'in_response_to', 'response_type'])

            for dates in miss_dates:
                date_from = dates - pd.DateOffset(days=2)
                date_to = dates + pd.DateOffset(days=2)
            
                newDetails.append({'coinname': coinName, 'start': date_from, 'end': date_to})
        
        #merging same dates dosen't seem necessary. But this can be optimized that way
        
        for i, detail in enumerate(newDetails):
            tDic = newDetails[i]
            tDic['keyword'] = self.coinKeywords[detail['coinname']]
            newDetails[i] = tDic
        
        return newDetails
#         hu = historicDownloader()
#         hu.perform_scraping()