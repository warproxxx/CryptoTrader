import pandas as pd
import numpy as np
import os.path

class TechnicalAnalysis:
    
    def merge_time(self, cache=False, save_cache=False):
        '''
        Merges the pandas dataframes by given Date. 
        
        Returns:
        dic (dict): Python Dictonary containing the dataframes merged for a given Date
        '''
        dic = {}
        fromval = 0
        toval = 0
        
        for i in self.Timeframe:
            dic[str(i) + "hour"] = pd.DataFrame(self.df.iloc[0:0])
        
        for i in self.Timeframe:

            currname = str(i) + "hour"

            fname = 'cache-{}-{}.csv'.format(self.coinname, str(i) + "merged")
            fullname = 'TechnicalAnalysis\cache\{}'.format(fname)

            if (cache == True and os.path.isfile(fullname)):
                print('Read merged data from cache')
                dic[currname] = pd.read_csv(fullname,index_col='Date') 

            else:
                for j in range(0, self.df.shape[0], i):
                    tempdf = self.df.iloc[j:j+i]
                    dic[currname] = dic[currname].append({'Date': tempdf.index[0], 'Open': tempdf.iloc[0]['Open'], 'Close': tempdf.iloc[-1]['Close'], 'High': max(tempdf['High']), 'Low': min(tempdf['Low']), 'Volume': sum(tempdf['Volume']), 'Classification': tempdf.iloc[-1]['Classification'], 'Percentage Change': tempdf.iloc[-1]['Percentage Change']}, ignore_index=True) #append returns a new dataframe
            
                dic[currname].set_index('Date', inplace=True)  
                dic[currname].index = dic[currname].index.map(int) #convert to int because getting floats in scientific notation
                dic[currname]['Classification'] = dic[currname]['Classification'].astype(int)

                if (cache == True or save_cache == True):
                    dic[currname].to_csv(fullname)
                    print('Wrote {} to cache'.format(fname))

        self.dic = dic
        
    def set_dic(self, dic):
        '''
        Dictionary stores dataframes at different Timeframe and periods with specified Technical Indicators
        
        This function updates that dictionary
        
        Parameters:
        ___________
        dic: (dict)
        New Dictionary to update with
        
        '''
        self.dic = dic
        
    def get_dic(self):
        '''
        Returns the current dictionary which stores dataframes at different Timeframe and periods with specified Technical Indicators 
        
        Returns:
        ________
        dic: (dict)
        Dictionary which stores dataframes at different Timeframe and periods with specified Technical Indicators 
        
        '''
        return self.dic
    
    def get_dataframe(self):
        '''
        Returns values of dictionary placed in the initial dataframe. All dictonaries are merged into a single dataframe with many columns
        '''
        for key,df in self.dic.items():

            diff = df.columns.symmetric_difference(self.initial_cols).drop('Date')
            columns = df[diff].columns
            new_name = key + columns
            
            required_df = df[columns]
            required_df.columns = new_name
            
            try:
                self.df = self.df.set_index('Date')
            except:
                pass

            try:
                required_df = required_df.set_index('Date')
            except:
                pass
            
            self.df = pd.concat([self.df, required_df], axis=1)
            self.df.fillna(method='ffill', inplace=True)
            
        return self.df
    
    def perform(self, method):
        '''
        Binding Function as loop code is repeated in all tecnical analysis. Calls the technical analysis functions for each datafram in dictionary
        
        Parameters:
        ___________
        method_name: (string)
        Possible Values: macd, rsi, bollingerband, obv, volumechange, parablicsar
        '''
        
        for key,df in self.dic.items():
            for period in self.period:
                if method in self.method_list:
                    if (method == 'macd' or method == 'rsi' or method == 'bollingerband'):
                        ret = self.method_list[method](df['Close'], key, period)
                        self.dic[key][method + str(period)] = ret #set the value to dictionary
                    elif (method == 'obv' or method == 'volumechange'):
                        ret = self.method_list[method](df, key, period)
                        
                        if (method == 'obv'):
                            self.dic[key][method] = ret #because obv is today vs yesterday
                        else:
                            self.dic[key][method + str(period)] = ret #set the value to dictionary
                    else:
                        print("That function does not exist in the conditions. Check the code")
                else:
                    raise Exception("Method %s not found" % method)
    
    def macd(self, close, key, period):
        '''
        Calculates Moving Average Convergance Divergence (MACD) and adds it in the dictionary
        
        It is the difference of moving average between 2 different Timeframes
        
        Eg:
        MACD14 means EWMA12 - EWMA26 and so on
        
        Source: https://sci-hub.hk/https://doi.org/10.1016/j.jfds.2016.03.002
        '''
        ewma1 = period - 2
        ewma2 = (period * 2) - 2

        e1 = close.ewm(span=ewma1).mean()
        e2 = close.ewm(span=ewma2).mean()

        return (e1 - e2)

    def rsi(self, close, key, period):
        '''
        Calculates Relative Strength Index (RSI) using simple average
        RSI = 100 - (100 / (1 + RS))
        
        where RS = (Average of t day ups closes / Average of t day s down closes)
        Source: https://sci-hub.hk/https://doi.org/10.1016/j.jfds.2016.03.002, https://stackoverflow.com/questions/20526414/relative-strength-index-in-python-pandas
        
        '''
        diff = close.diff().fillna(method='bfill')     

        up_close, down_close = diff.copy(), diff.copy()

        up_close[up_close < 0] = 0
        down_close[down_close > 0] = 0

        up = up_close.rolling(period, min_periods=1).mean()
        down = down_close.abs().rolling(period, min_periods=1).mean()

        return (100.0 - (100.0 / (1.0 + (up / down))))
    
    def bollingerband(self, close, key, period):
        '''
        Calculates a number typically between -1 and 1 that denotes the bollinger band character
        
        Source: https://classroom.udacity.com/courses/ud501/lessons/4441149454/concepts/44358802960923

        Bollinger Band = (price - SMA) / (2 * std) 
        '''
        rolling = close.rolling(period, min_periods=1)
        bb = (close - rolling.mean())/(2 * rolling.std())
        bb = bb.fillna(method='bfill')
        
        return bb
    
    def obv(self, df, key, period):
        '''
        Calculates On Balance Volume (OBV)
        
        Source: https://www.investopedia.com/terms/o/onbalancevolume.asp
        
        close today > close yesterday Current OBV = Previous OBV + today's volume
        close today < close yesterday Current OBV = Previous OBV - today's volume
        close today = close yesterday Current OBV = Previous OBV
        '''
        tempdf = df.copy()
        tempdf['obv'] = 0

        for index, row in tempdf.iterrows():
            if 'oldloc' in vars() or 'oldloc' in globals():
                if tempdf.loc[index]['Close'] > tempdf.loc[oldloc]['Close']:
                    tempdf.at[index, 'obv'] = tempdf.loc[oldloc]['obv'] + tempdf.loc[index]['Volume']
                elif tempdf.loc[index]['Close'] < tempdf.loc[oldloc]['Close']:
                    tempdf.at[index, 'obv'] = tempdf.loc[oldloc]['obv'] - tempdf.loc[index]['Volume']
                elif tempdf.loc[index]['Close'] == tempdf.loc[oldloc]['Close']:
                    tempdf.at[index, 'obv'] = tempdf.loc[oldloc]['obv']
                        
            oldloc = index
        
        return tempdf['obv']                
    
    def volumechange(self, df, key, period):
        '''
        Calculates the rate of change of volume
        
        VROC = (Most recent closing volume - Volume n periods ago) / Closing volume n periods ago x 100
        If there is no 14 day old, then latest
        '''
        roc = df['Volume'].pct_change(periods=period, fill_method='bfill')
        roc.fillna(0, inplace=True)
        roc = roc.replace(np.inf, 0)
        return roc
            
    def __init__(self, df, Timeframe = [3, 6, 24], period=[14], coin='DEF'):
        '''
        Parameters:
        ___________
        
        df: Pandas dataframe containing Open, Close, High, Low and Volume
        Timeframe (optional): list containing Timeframes (hours for hourly data) to merge and calculate in
        period: (optional): list containing periods to calculate in for a given Timeframe
        coinname (optional): to manage caching
        '''
        self.df = df
        self.Timeframe = Timeframe
        self.period = period
        self.method_list = {'macd': self.macd, 'bollingerband': self.bollingerband, 'obv': self.obv, 'volumechange': self.volumechange, 'rsi': self.rsi}
        self.initial_cols = df.columns
        self.coinname = coin