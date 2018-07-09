import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
from sklearn.utils import shuffle
import math
import os

class PriceFunctions():
    def percentage_to_classification(self, x):
        #returns 1 or 0 depending on whether the price went up or down 
        y = 0
        
        if (x >= 0):
            y = 1
        else:
            y = 0
            
        return y
    
    def get_numpy(self, pd_Xtrain, pd_ytrain, pd_Xtest, pd_ytest):
        '''
        Normalized numpy from pandas
        
        Arguments:
        pd_Xtrain: Unnormalized X train as pandas
        pd_ytrain: Unnormalized y train as pandas
        pd_Xtest: Unnormalized X test as pandas
        pd_ytest: Unnormalized y test as pandas
        
        Returns:
        mean: pandas mean of training set
        std: pandas std of training set
        Xtrain: Normalized pandas to numpy
        ytrain: Normalized pandas to numpy
        Xtest: Normalized pandas to numpy
        ytest: Normalized pandas to numpy
        '''
        
        mean = pd_Xtrain.mean()
        std = pd_Xtrain.std()

        pd_XtrainNorm = (pd_Xtrain - mean)/std
        pd_XtestNorm = (pd_Xtest - mean)/std
    
        Xtrain = np.array(pd_XtrainNorm)
        ytrain = np.array(pd_ytrain).astype(np.float32)

        Xtest = np.array(pd_XtestNorm) 
        ytest = np.array(pd_ytest).astype(np.float32)
        
        return mean, std, Xtrain, ytrain, Xtest, ytest
    
    def to_same_starting(self, dfs):
        '''
        dfs: (dict)
        Dictionary containing 

        Converts dataframes to same starting and ending date
        '''
        biggest = 1
        smallestFinal = 99999999999
        for coin in dfs:
            if dfs[coin].index[0] > biggest:
                biggest = dfs[coin].index[0]

            if dfs[coin].index[-1] < smallestFinal:
                smallestFinal = dfs[coin].index[-1]

        
        for coin in dfs:        
            dfs[coin] = dfs[coin][dfs[coin].index >= biggest]
            dfs[coin] = dfs[coin][dfs[coin].index <= smallestFinal] 

        return dfs

    def to_usd(self, dfs):
        '''
        Uses the bitcoin column to convert other to USD. BTC should be first column
        '''
        cols = list(dfs.keys())
        cols.remove('BTC')

        for coin in cols:
            dfs[coin]['Open'] = dfs[coin]['Open'] * dfs['BTC']['Open'] 
            dfs[coin]['Close'] = dfs[coin]['Close'] * dfs['BTC']['Close']
            dfs[coin]['High'] = dfs[coin]['High'] * dfs['BTC']['Close']  #some issue in logic
            dfs[coin]['Low'] = dfs[coin]['Low'] * dfs['BTC']['Close'] #some issue in logic

        return dfs

    def add_yColumns(self, dfs, targetdays=24, absolute=True, dateindex = True):
        '''
        Parameters:
        dfs: (dictionary)
        Dictionary containing coins and their price values
        
        targetdays: (int) (optional)
        specify the target number of timeframe from which percentage change is to be calculated. 24 for daily change in hourly. 1 for daily change in daily 
        
        negative: (boolean) (optional)
        If set to true, absolute value of percentage change is returned

        dateindex: (boolean) (optional)
        If true set date as index
        
        Returns:
        
        df: 
        pandas dataframe of data from bitfinex
        '''
        targetdays = -1 * targetdays

        for key,df in dfs.items():

            if (dateindex == True):
                df.set_index('Date', inplace=True)

            df['Percentage Change'] = (1 - df['Close']/df.shift(targetdays)['Close'])
            df['Classification'] = df['Percentage Change'].apply(PriceFunctions().percentage_to_classification)
            
            df['Classification'] = df['Classification'].astype(np.float32)
            df['Percentage Change'] = df['Percentage Change'].astype(np.float32)
            
            if (absolute == True):
                df['Percentage Change'] = df['Percentage Change'].abs()
            
            df = df[:targetdays]

            dfs[key] = df
        
        return dfs
    
    def split_traintest(self, df, ratio=0.83):
        '''
        Parameters:
        df: dataframe to split into training and test set
        ratio (int optional): The size of training set in percentage
        
        
        Returns:
        pd_Xtrain: Unnormalized X train as pandas
        pd_ytrain: Unnormalized y train as pandas
        pd_Xtest: Unnormalized X test as pandas
        pd_ytest: Unnormalized y test as pandas
        '''
        
        trainTill = math.floor(ratio * df.shape[0])
        dfTraining = df[:trainTill]
        dfTest = df[trainTill:]
        
        pd_ytrain = dfTraining[['Classification', 'Percentage Change']]
        pd_Xtrain = dfTraining.drop(['Classification', 'Percentage Change'], axis=1)
        
        pd_ytest = dfTest[['Classification', 'Percentage Change']]
        pd_Xtest = dfTest.drop(['Classification', 'Percentage Change'], axis=1)
        
        #to be compatible with the backtest code
        pd_Xtrain['Date'] = pd_Xtrain.index
        pd_Xtest['Date'] = pd_Xtest.index
        pd_Xtrain.reset_index(drop = True, inplace = True)
        pd_Xtest.reset_index(drop = True, inplace = True)
        
        return pd_Xtrain, pd_ytrain, pd_Xtest, pd_ytest