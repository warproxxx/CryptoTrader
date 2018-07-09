import pandas as pd
import datetime
import os
import numpy as np

import CryptoScraper

class manipulateData:
    def __init__(self, length, coin):
        self.length = length
        self.currDir = os.path.dirname(CryptoScraper.__file__)
        self.coin = coin

    def get_custom_timeframe(self):
        hourlyDf = pd.read_csv(os.path.dirname(CryptoScraper.__file__) + '/cache/{}.csv'.format(self.coin))

        if (self.length == 1):
            return hourlyDf
        else:
            newDf = self.merge_data(hourlyDf)
            return newDf

    def merge_data(self, df):
        df['new'] = pd.to_datetime(df['Date'], unit='s')
        df = df.set_index(df['new'])

        df=df.resample('{}H'.format(self.length)).agg({'Date': lambda x: x.iloc[0], 'Open': lambda x: x.iloc[0], 'Close': lambda x: x.iloc[-1], 'High': np.max, 'Low': np.min, 'Volume': np.sum})
        df=df.reset_index(drop=True)
        
        return df