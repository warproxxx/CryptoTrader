import os
from glob import glob
import sys

import pandas as pd
import numpy as np

import swifter
import numba
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

    def __init__(self, detailsList, algo_name, relative_dir=""):
        '''
        Parameters:
        ___________
        detailsList (list): 
        List containing keyword, coinname in string and start and end in date format. For looping

        algo_name (string):
        The name of the algorithm so as to save in file

        relative_dir (string):
        The relative directory 
        '''
        _, currRoot_dir = get_locations()

        self.logger = get_logger(os.path.join(currRoot_dir, "/logs/historicprocess.log"))

        self.detailsList = detailsList
        self.algo_name = algo_name

        self.historic_path = os.path.join(currRoot_dir, relative_dir, "data/tweet/{}/historic_scrape")

    def read_merge(self, delete=True):
        '''
        Reads many csv files and combines them to one

        Paramters:
        _________
        delete (boolean): Deletes the read file later if set to true
        '''

        for coinDetail in self.detailsList:
            path = os.path.join(self.historic_path.format(coinDetail['coinname']), "raw")

            files = glob(path + "/*")
            f = merge_csvs(files, ignore_name="combined")

            if f != None:
                if (delete==True):
                    for file in files:
                        os.remove(file)

                with open(os.path.join(path, "combined.csv"), "wb") as out:
                    out.write(f.read())

    def clean_data(self):
        '''
        Cleans the csv file. Fillna, drop duplicates and such
        '''
        for coinDetail in self.detailsList:
            fileRead = os.path.join(self.historic_path.format(coinDetail['coinname']), "raw/combined.csv")
            
            if (os.path.isfile(fileRead)):
                df = pd.read_csv(fileRead)
                df = df.dropna().sort_values('Likes', ascending=False).drop_duplicates('ID').sort_values('Time').reset_index(drop=True)
                df.to_csv(fileRead, index=None)
                self.logger.info("Saved cleaned data to {}".format(fileRead))

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

        try:
            t = x.index[0]
            y['Time'] = pd.Timestamp("{}-{}-{} {}:00:00".format(t.year, t.month, t.day, t.hour))
        except:
            pass
    
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
            savePath = os.path.join(self.historic_path.format(coinDetail['coinname']), "interpreted/data-{}.csv".format(self.algo_name))

            if (not(os.path.isfile(savePath))):
                path = os.path.join(self.historic_path.format(coinDetail['coinname']), "raw")

                combinedCsv = os.path.join(path, "combined.csv")

                if os.path.isfile(combinedCsv):
                    df = pd.read_csv(combinedCsv, lineterminator='\n')
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
                    df['Time'] = pd.date_range(df['Time'].iloc[0], df['Time'].iloc[-1], periods=df['Time'].shape[0])
                    self.logger.info("Features Calculated")
                    
                    df['variation_all'] = df['n_bullish_all'].diff()
                    df = df.drop(['n_bullish_all', 'n_bearish_all'], axis=1)
                    df['mean_vader_change_top'] = df['mean_vader_top'].diff()
                    #add botorNot too
                    df = trends_ta(df, 'mean_vader_top')
                    df = trends_ta(df, 'mean_vader_all')
                    df = df.replace(np.inf, 0)
                    df = df.replace(-np.inf, 0)
                    df = df.replace(np.nan, 0)
                    
                    df.to_csv(savePath, index=None)
                    self.logger.info("Added all features. Saved to {}".format(savePath))
                else:
                    self.logger.info("{} does not exists so skipping".format(combinedCsv))
            else:
                self.logger.info("Using the cached file from {}".format(savePath))

    def create_visualization_features(self):
        pass

class profileProcessor:
    def __init__(self, detailsList, relative_dir=""):
        '''
        Parameters:
        ___________
        detailsList (list): 
        List containing keyword, coinname in string and start and end in date format. For looping

        relative_dir (string):
        The relative directory 
        '''
        _, currRoot_dir = get_locations()

        self.logger = get_logger(os.path.join(currRoot_dir, "logs/profileprocess.log"))
        self.detailsList = detailsList
        self.profile_path = os.path.join(currRoot_dir, relative_dir, "data/profile")

    @numba.jit
    def clean_data(self):
        '''
        Cleans the csv file. Fillna, drop duplicates and such
        '''
        live_userData_dir = os.path.join(self.profile_path, "live/userData.csv")
        live_userTweets_dir = os.path.join(self.profile_path, "live/userTweets.csv")

        processed_userData_dir = os.path.join(self.profile_path, "storage/raw/userData.csv")
        processed_userTweets_dir = os.path.join(self.profile_path, "storage/raw/userTweets.csv")

        userData = pd.read_csv(live_userData_dir, low_memory=False)
        
        try:
            userData=pd.concat([userData, pd.read_csv(processed_userData_dir, low_memory=False)])
        except:
            pass
        
        self.logger.info("User Data Read")
        
        userTweets = pd.read_csv(live_userTweets_dir, low_memory=False)
        
        try:
            userTweets=pd.concat([userTweets, pd.read_csv(processed_userTweets_dir, low_memory=False)])
        except:
            pass

        self.logger.info("User Tweets Read")
        
        userTweets = userTweets.rename(columns={'User': 'username'})

        merged = pd.merge(userData, userTweets, how='inner', on=['username'])
        self.logger.info("Inner Merged Done")
        
        newuserData = merged[userData.columns]
        newuserData = newuserData.set_index('username').drop_duplicates().reset_index()

        newuserTweets = merged[userTweets.columns]
        newuserTweets = newuserTweets.rename(columns={'username': 'User'})

        newuserTweets = newuserTweets.set_index(['User', 'ID']).drop_duplicates().reset_index()
        
        self.logger.info("All done saving")

        newuserData.to_csv(processed_userData_dir, index=None)
        self.logger.info("userData.csv has been updated and moved")
        os.remove(live_userData_dir)
        self.logger.info("Deleting userData.csv in the live folder")
        
        newuserTweets.to_csv(processed_userTweets_dir, index=None)
        self.logger.info("userTweets.csv has been updated and moved")
        os.remove(live_userTweets_dir)
        self.logger.info("Deleting userTweets.csv in the live folder")
        
        newuserData['username'].to_csv(os.path.join(self.profile_path, "extractedUsers.csv"), index=None)
        self.logger.info("extractedUsers.csv has been updated")
        os.remove(os.path.join(self.profile_path, "live/userData.csv"))
        self.logger.info("Deleting extractedUsers.csv in the live folder")


    def create_ml_features(self):
        '''
        Create features from these data
        '''
        pass