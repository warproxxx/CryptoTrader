import os
from glob import glob
import sys

import pandas as pd
import numpy as np

import swifter
from multiprocessing import Pool, cpu_count

import nltk
from nltk.sentiment import vader

from libs.writing_utils import get_locations, get_logger
from libs.reading_utils import cleanData

sys.path.append(os.path.dirname(get_locations()[1]))

from common_modules.common_utils import merge_csvs, trends_ta

def applyVader(x, analyzer):
    return analyzer.polarity_scores(x)['compound']

def applyParallel(dfGrouped, func):
    with Pool(cpu_count()) as p:
        ret_list = p.map(func, [group for name, group in dfGrouped])
        
    return pd.DataFrame(ret_list)

class historicProcessor:
    '''
    Processor for historic data
    '''

    def __init__(self, detailsList, relative_dir="/", logger=None):
        '''
        Parameters:
        ___________
        detailsList (list): 
        List containing keyword, coinname in string and start and end in date format

        relative_dir (string):
        The relative directory 
        '''
        _, self.currRoot_dir = get_locations()

        if logger == None:
            self.logger = get_logger(self.currRoot_dir + "/logs/process.log")
        else:
            self.logger = logger

        self.detailsList = detailsList
        self.relative_dir = relative_dir

    def read_merge(self, delete=True):
        '''
        Reads many csv files and combines them to one

        Paramters:
        _________
        delete (boolean): Deletes the read file later if set to true
        '''

        for coinDetail in self.detailsList:
            path = os.path.join(self.currRoot_dir, self.relative_dir, "data/tweet/{}/historic_scrape/raw".format(coinDetail['coinname']))

            files = glob(path + "/*")
            f = merge_csvs(files, ignore_name="combined.csv")

            if (delete==True):
                for file in files:
                    os.remove(file)

            with open(os.path.join(path, "combined.csv"), "wb") as out:
                out.write(f.read())

    def f_add_features(self, x):
        '''
        Calcualtes features based on the data

        Parameters:
        ___________
        x (part of dataframe):
        The group which should be merged

        Returns:
        _______
        y (dataframe):
        Feature calculated from the data
        '''
        y = pd.Series()
    
        x = x.assign(f = x['Likes'] + x['Replies'] + x['Retweets']).sort_values('f', ascending=False).drop('f', axis=1)
        
        Nbullish = sum(x['sentiment'] > 0) #should use something else later
        Nbearish = sum(x['sentiment'] < 0)
        
        y['mean_vader_all'] = x['sentiment'].mean()
        
        #doi.org/10.1016/j.eswa.2016.12.036
        y['n_bullish_all'] = Nbullish
        y['n_bearish_all'] = Nbearish
        
        try:
            y['bullish_ratio_all'] = Nbullish / (Nbullish + Nbearish)
        except:
            y['bullish_ratio_all'] = np.nan
        
        try:
            y['bearish_ratio_all'] = Nbearish / (Nbullish + Nbearish)
        except:
            y['bearish_ratio_all'] = np.nan
            
        y['bullish_index_all'] = np.log((Nbullish + 1)/(Nbearish + 1))
        
        try:
            y['agreement_all'] = 1 - np.sqrt(1-(((Nbullish - Nbearish)/(Nbullish + Nbearish))**2) )
        except:
            y['agreement_all'] = np.nan
            
        try:
            y['spread_all'] = (Nbullish - Nbearish)/(Nbullish + Nbearish)
        except:
            y['spread_all'] = np.nan
        
        xTopAll = x.iloc[:int(x.shape[0] * .15)]
        
        y['mean_vader_top'] = xTopAll['sentiment'].mean()
        y['mean_likes_top'] = xTopAll['Likes'].mean()
        y['mean_replies_top'] = xTopAll['Replies'].mean()
        y['mean_retweets_top'] = xTopAll['Retweets'].mean()
        
        return y

    def create_ml_features(self):
        '''
        Create features from these textual data
        '''

        for coinDetail in self.detailsList:
            path = os.path.join(self.currRoot_dir, self.relative_dir, "data/tweet/{}/historic_scrape/raw".format(coinDetail['coinname']))
            df = pd.read_csv(os.path.join(path, "combined.csv"), lineterminator='\n')
            self.logger.info("CSV file read for {}".format(coinDetail['coinname']))

            df['Tweet'] = cleanData(df['Tweet'])
            self.logger.info("Tweets Cleaned")
            
            df['Time'] = pd.to_datetime(df['Time'], unit='s')
            df = df.set_index('Time')
            
            self.logger.info("Calculating sentiment")
            analyzer = vader.SentimentIntensityAnalyzer()
            df['sentiment'] = df['Tweet'].swifter.apply(applyVader, analyzer=analyzer)

            self.logger.info("Now calculating features")
            df = applyParallel(df.groupby(pd.Grouper(freq='H')), self.f_add_features)
            
            self.logger.info("Features Calculated")
            
            df['variation_all'] = df['n_bullish_all'].diff()
            df = df.drop(['n_bullish_all', 'n_bearish_all'], axis=1)
            df['mean_vader_change_top'] = df['mean_vader_top'].diff()
            #add botorNot too
            df = trends_ta(df, 'mean_vader_top')
            df = trends_ta(df, 'mean_vader_all')
            df = df.replace(np.nan, 0)
            savePath = os.path.join(self.currRoot_dir, self.relative_dir, "data/tweet/{}/historic_scrape/interpreted/data.csv".format(coinDetail['coinname']))
            df.to_csv(savePath)
            self.logger.info("Added all features. Saved to {}".format(savePath))

    def create_visualization_features(self):
        pass