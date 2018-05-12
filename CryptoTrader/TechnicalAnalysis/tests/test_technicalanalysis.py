import pandas as pd
import numpy as np

from TechnicalAnalysis import TechnicalAnalysis

class TestTechnicalAnalysis():
    
    #run before test
    def setup_method(self, test_method): 
        self.shape_df = pd.DataFrame(columns=['Date', 'Open', 'Close', 'High', 'Low', 'Volume'])
        
        #might be better if there are negatives and positives too in different part. Do it.
        for i in range(100):
            self.shape_df = self.shape_df.append({'Date': i, 'Open': i, 'Close': i, 'High': i, 'Low': i, 'Volume': i, 'Classification':i, 'Percentage Change': i}, ignore_index=True)
        
        self.shape_df.set_index('Date', inplace=True)
        
        symmetry_df = pd.DataFrame(columns=['Date', 'Open', 'Close', 'High', 'Low', 'Volume'])
        symmetry_df = symmetry_df.append({'Date': 1, 'Open': 3, 'Close': 1, 'High': 5, 'Low': 0, 'Volume': 10, 'Classification': 0, 'Percentage Change': 0.2}, ignore_index=True)
        symmetry_df = symmetry_df.append({'Date': 2, 'Open': 1, 'Close': 8, 'High': 8, 'Low': 1, 'Volume': 10, 'Classification': 1, 'Percentage Change': 0.11}, ignore_index=True)
        symmetry_df = symmetry_df.append({'Date': 3, 'Open': 8, 'Close': 4, 'High': 8, 'Low': 4, 'Volume': 10, 'Classification': 0, 'Percentage Change': 0.003}, ignore_index=True)
        symmetry_df = symmetry_df.append({'Date': 4, 'Open': 4, 'Close': 6, 'High': 6, 'Low': 4, 'Volume': 10, 'Classification': 1, 'Percentage Change': 0.003}, ignore_index=True)
        symmetry_df = symmetry_df.append({'Date': 5, 'Open': 6, 'Close': 10, 'High': 10, 'Low': 6, 'Volume': 10, 'Classification': 0, 'Percentage Change': 0.001}, ignore_index=True)
        symmetry_df = symmetry_df.append({'Date': 6, 'Open': 10, 'Close': 3, 'High': 10, 'Low': 2, 'Volume': 10, 'Classification': 0, 'Percentage Change': 0.004}, ignore_index=True)
        symmetry_df = symmetry_df.append({'Date': 7, 'Open': 3, 'Close': 4, 'High': 4, 'Low': 2, 'Volume': 10, 'Classification': 1, 'Percentage Change': 0.09}, ignore_index=True)
        symmetry_df = symmetry_df.append({'Date': 8, 'Open': 4, 'Close': 8, 'High': 14, 'Low': 3, 'Volume': 10, 'Classification': 0, 'Percentage Change': 0.1}, ignore_index=True)
        symmetry_df = symmetry_df.append({'Date': 9, 'Open': 8, 'Close': 12, 'High': 12, 'Low': 1, 'Volume': 10, 'Classification': 1, 'Percentage Change': 0.2}, ignore_index=True)
        
        self.symmetry_df = symmetry_df
    
    def test_merge_time(self):
        ta = TechnicalAnalysis(self.shape_df, Timeframe=[5, 10])
        ta.merge_time()
        dic = ta.get_dic()
        
        assert(len(dic) == 2)
        
        assert('5hour' in dic)
        assert('10hour' in dic)

        assert(dic['5hour'].shape[0] == 20)
        assert(dic['10hour'].shape[0] == 10)
        
        assert(sum(dic['5hour'].index / 5) == sum(np.arange(0, 20, 1)))
        assert(sum(dic['10hour'].index / 10) == sum(np.arange(0, 10, 1)))
        
        del ta
        
        #now tests for open, close, high, low, volume
                
        ta2 = TechnicalAnalysis(self.symmetry_df, Timeframe=[3])
        ta2.merge_time()
        dicc = ta2.get_dic()
        
        assert(dicc['3hour'].iloc[0]['Open'] == 3)
        assert(dicc['3hour'].iloc[0]['Close'] == 4)
        assert(dicc['3hour'].iloc[0]['High'] == 8)
        assert(dicc['3hour'].iloc[0]['Low'] == 0)
        assert(dicc['3hour'].iloc[0]['Volume'] == 30)
        
        assert(dicc['3hour'].iloc[1]['Open'] == 4)
        assert(dicc['3hour'].iloc[1]['Close'] == 3)
        assert(dicc['3hour'].iloc[1]['High'] == 10)
        assert(dicc['3hour'].iloc[1]['Low'] == 2)
        assert(dicc['3hour'].iloc[1]['Volume'] == 30)
        
        assert(dicc['3hour'].iloc[2]['Open'] == 3)
        assert(dicc['3hour'].iloc[2]['Close'] == 12)
        assert(dicc['3hour'].iloc[2]['High'] == 14)
        assert(dicc['3hour'].iloc[2]['Low'] == 1)
        assert(dicc['3hour'].iloc[2]['Volume'] == 30)
        
        del ta2
    
    def test_macd(self):
        dic = {}
        dic['1hour'] = self.symmetry_df
        
        ta = TechnicalAnalysis(self.symmetry_df, Timeframe=[3])
        ta.set_dic(dic)
        ta.perform('macd')
        dic = ta.get_dic()
        
        assert('macd14' in dic['1hour'])
        assert(dic['1hour'].iloc[0]['macd14'] < dic['1hour'].iloc[1]['macd14']) #as close rises
        assert(dic['1hour'].iloc[1]['macd14'] > dic['1hour'].iloc[2]['macd14']) #as close falls
        assert(dic['1hour'].iloc[2]['macd14'] > dic['1hour'].iloc[0]['macd14']) #as close is bigger than 0 even though its falling
    
    def test_rsi(self):
        dic = {}
        dic['1hour'] = self.symmetry_df
        
        ta = TechnicalAnalysis(self.symmetry_df, Timeframe=[3])
        ta.set_dic(dic)
        ta.perform('rsi')
        dic = ta.get_dic()
        
        assert(sum(~((dic['1hour']['rsi14'] <=100) &  (dic['1hour']['rsi14'] >=0))) == 0)
        assert(dic['1hour'].iloc[1]['rsi14'] > dic['1hour'].iloc[2]['rsi14'])
        assert(dic['1hour'].iloc[2]['rsi14'] < dic['1hour'].iloc[3]['rsi14'])
        
    def test_bollingerband(self):
        dic = {}
        dic['1hour'] = self.symmetry_df

        ta = TechnicalAnalysis(self.symmetry_df, Timeframe=[3])
        ta.set_dic(dic)
        ta.perform('bollingerband')
        dic = ta.get_dic()

        assert(sum(~((dic['1hour']['bollingerband14'] <= 1) &  (dic['1hour']['bollingerband14'] >= -1))) == 0)
        assert(dic['1hour'].iloc[1]['bollingerband14'] > dic['1hour'].iloc[2]['bollingerband14'])
        assert(dic['1hour'].iloc[2]['bollingerband14'] < dic['1hour'].iloc[3]['bollingerband14'])
    
    def test_obv(self): #obv is today vs yesterday
        dic = {}
        dic['1hour'] = self.symmetry_df

        ta = TechnicalAnalysis(self.symmetry_df, Timeframe=[3])
        ta.set_dic(dic)
        ta.perform('obv')
        dic = ta.get_dic()
        
        assert(dic['1hour'].iloc[1]['obv'] > dic['1hour'].iloc[0]['obv'])
        assert((dic['1hour'].iloc[1]['obv'] - dic['1hour'].iloc[2]['obv']) == 10)
        assert((dic['1hour'].iloc[3]['obv'] - dic['1hour'].iloc[2]['obv']) == 10)
        assert((dic['1hour'].iloc[4]['obv'] - dic['1hour'].iloc[3]['obv']) == 10)
    
    def test_volumechange(self):
        dic = {}
        dic['1hour'] = self.shape_df

        ta = TechnicalAnalysis(self.shape_df, Timeframe=[3])
        ta.set_dic(dic)
        ta.perform('volumechange')
        dic = ta.get_dic()

        assert(sum(~((dic['1hour']['volumechange14'] <= 100) &  (dic['1hour']['volumechange14'] >= -100))) == 0)
    
    def test_perform(self):
        '''
        Testing doing multiple strategies and periods
        '''
        Timeframe=[3,4]
        period=[3,4,5]
        
        ta = TechnicalAnalysis(self.shape_df, Timeframe=Timeframe, period=period)
        ta.merge_time()
        
        ta.perform('macd')
        ta.perform('bollingerband')
        ta.perform('volumechange')
        ta.perform('rsi')
        ta.perform('obv')
        
        df = ta.get_dataframe() #the different Timeframes should be merged into single dataframe
        cols = pd.Series(df.columns) #simple multiply won't work in assert as obv is not divided into different Timeframe
        
        assert(len(cols[cols.str.contains('macd')]) == len(Timeframe) * len(period))
        assert(len(cols[cols.str.contains('macd') & cols.str.contains('3hour')]) == 3)
        assert(len(cols[cols.str.contains('macd') & cols.str.contains('4hour')]) == 3)
        
        assert(len(cols[cols.str.contains('bollingerband')]) == len(Timeframe) * len(period))
        assert(len(cols[cols.str.contains('bollingerband') & cols.str.contains('3hour')]) == 3)
        assert(len(cols[cols.str.contains('bollingerband') & cols.str.contains('4hour')]) == 3)
        
        assert(len(cols[cols.str.contains('volumechange')]) == len(Timeframe) * len(period))
        assert(len(cols[cols.str.contains('volumechange') & cols.str.contains('3hour')]) == 3)
        assert(len(cols[cols.str.contains('volumechange') & cols.str.contains('4hour')]) == 3)
        
        assert(len(cols[cols.str.contains('rsi')]) == len(Timeframe) * len(period))
        assert(len(cols[cols.str.contains('rsi') & cols.str.contains('3hour')]) == 3)
        assert(len(cols[cols.str.contains('rsi') & cols.str.contains('4hour')]) == 3)
        
        assert(len(cols[cols.str.contains('obv')]) == len(Timeframe))
        
    #run after test
    def teardown_method(self, test_method):
        del self.shape_df
        del self.symmetry_df