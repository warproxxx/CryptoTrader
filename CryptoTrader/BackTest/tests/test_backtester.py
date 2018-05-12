import quandl
import pandas as pd
import numpy as np
from data_utils import BasicFunctions, PriceFunctions

from BackTest import Backtester

class TestBacktester:
    def setup_method(self, test_method): 
        
        np.random.seed(1)
        self.idx = ['Date', 'Coin', 'Price', 'Bankroll', 'Amount', 'Type', 'Position', 'Status']
        self.bars = {}
        self.signals = {}
        
        for i in ['BTC', 'ETH']:
            self.bars[i] = pd.read_csv('BackTest/tests/{}_test.csv'.format(i))
            self.bars[i]['Percentage'] = np.random.uniform(low=-0.2, high=0.2, size=self.bars[i].shape[0])
            self.bars[i]['Classification'] = self.bars[i]['Percentage'].apply(PriceFunctions().percentage_to_classification)
            self.bars[i]['Classification'] = self.bars[i]['Classification'].apply(lambda x: np.random.uniform(low=0, high=0.5) if x == 0 else np.random.uniform(low=0.5, high=1)) #adding randomness to classification

            self.signals[i] = np.asarray(self.bars[i][['Classification', 'Percentage']])
            self.bars[i]['Percentage'] = np.absolute(self.bars[i]['Percentage'])

            self.bars[i].drop(['Percentage', 'Classification'], axis=1, inplace=True)
            
            for keys in self.bars:
                self.bars[keys]['Date'] = pd.to_datetime(self.bars[keys]['Date'])
                
        
    def get_dataframe(self):
        
        
        #bankroll currently contains new value after position is opened
        df = pd.DataFrame(columns=self.idx)
        df = df.append(pd.Series([0, 'BTC', 1000, 8000, 2000, 'OPEN', 'LONG', 'INACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([1, 'BTC', 1000, 6000, 2000, 'OPEN', 'LONG', 'INACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([2, 'BTC', 1000, 4000, 2000, 'OPEN', 'LONG', 'INACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([3, 'BTC', 1000, 10000, 6000, 'CLOSE', 'SHORT', 'INACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([4, 'BTC', 1000, 0, 10000, 'OPEN', 'LONG', 'INACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([5, 'BTC', 1000, 10000, 10000, 'CLOSE', 'SHORT', 'INACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([6, 'BTC', 1000, 20000, 10000, 'OPEN', 'SHORT', 'INACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([7, 'BTC', 1000, 10000, 10000, 'CLOSE', 'LONG', 'INACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([8, 'BTC', 1000, 9000, 1000, 'OPEN', 'LONG', 'ACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([9, 'BTC', 1000, 8000, 1000, 'OPEN', 'LONG', 'ACTIVE'], index=self.idx), ignore_index=True)
        
        return df
        
    def test_get_avilableamount(self):
        bt = Backtester(self.bars, self.signals)
        
        bt.set_positions(self.get_dataframe())
        
        assert(bt.get_avilableamount()[0]['long'] == 8000)
        assert(bt.get_avilableamount()[0]['short'] == 12000)
        
        df = pd.DataFrame(columns=self.idx)
        df = df.append(pd.Series([0, 'BTC', 1000, 8000, 2000, 'OPEN', 'LONG', 'INACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([1, 'BTC', 1000, 6000, 2000, 'OPEN', 'LONG', 'INACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([2, 'BTC', 1000, 4000, 2000, 'OPEN', 'LONG', 'INACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([3, 'BTC', 1000, 10000, 6000, 'CLOSE', 'SHORT', 'INACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([4, 'BTC', 1000, 20000, 10000, 'OPEN', 'SHORT', 'ACTIVE'], index=self.idx), ignore_index=True)
        bt.set_positions(df) 
        
        assert(bt.get_avilableamount()[0]['long'] == 20000)
        assert(bt.get_avilableamount()[0]['short'] == 0)
        
        df = pd.DataFrame(columns=self.idx)
        df = df.append(pd.Series([0, 'BTC', 1000, 12000, 2000, 'OPEN', 'SHORT', 'ACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([1, 'BTC', 1000, 14000, 2000, 'OPEN', 'SHORT', 'ACTIVE'], index=self.idx), ignore_index=True)
        bt.set_positions(df) 
        
        assert(bt.get_avilableamount()[0]['long'] == 14000)
        assert(bt.get_avilableamount()[0]['short'] == 6000)
        
        #This can't go negative it is going.
        
    def test_check_validity(self):
        bt = Backtester(self.bars, self.signals)
        bt.set_positions(self.get_dataframe())
        
        assert(bt.check_validity('LONG', 8000)['boolean'] == True)
        assert(bt.check_validity('LONG', 2000)['boolean'] == True)
        assert(bt.check_validity('LONG', 8001)['boolean'] == False)
        assert(bt.check_validity('LONG', 8001)['avilable'] == 8000)

        df = pd.DataFrame(columns=self.idx)
        df = df.append(pd.Series([0, 'BTC', 1000, 15000, 5000, 'OPEN', 'SHORT', 'ACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([1, 'BTC', 1000, 19000, 4000, 'OPEN', 'SHORT', 'ACTIVE'], index=self.idx), ignore_index=True)
        bt.set_positions(df)
        
        assert(bt.check_validity('LONG', 500)['boolean'] == True)
        assert(bt.check_validity('LONG', 19000)['boolean'] == True)
        assert(bt.check_validity('LONG', 19001)['boolean'] == False)
        assert(bt.check_validity('LONG', 19001)['avilable'] == 19000)

        assert(bt.get_avilableamount()[0]['long'] == 19000)
        assert(bt.get_avilableamount()[0]['short'] == 1000)
        
        df = pd.DataFrame(columns=self.idx)
        df = df.append(pd.Series([0, 'BTC', 1000, 13000, 3000, 'OPEN', 'SHORT', 'ACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([1, 'BTC', 1000, 15000, 2000, 'OPEN', 'SHORT', 'ACTIVE'], index=self.idx), ignore_index=True)
        bt.set_positions(df)
        
        assert(bt.check_validity('LONG', 15000)['boolean'] == True)
        assert(bt.check_validity('SHORT', 5000)['boolean'] == True)
        assert(bt.check_validity('SHORT', 5001)['boolean'] == False)
        assert(bt.check_validity('SHORT', 5001)['avilable'] == 5000)
        
    def test_close_reverse_position(self):
        bt = Backtester(self.bars, self.signals)
    
        df = pd.DataFrame(columns=self.idx)
        
        df = df.append(pd.Series([0, 'LTC', 1001, 10500, 500, 'OPEN', 'LONG', 'ACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([1, 'LTC', 1000, 10000, 500, 'OPEN', 'LONG', 'ACTIVE'], index=self.idx), ignore_index=True)
        
        df = df.append(pd.Series([2, 'BTC', 1001, 7500, 2500, 'OPEN', 'LONG', 'ACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([3, 'BTC', 1000, 5000, 2500, 'OPEN', 'LONG', 'ACTIVE'], index=self.idx), ignore_index=True)
        
        df = df.append(pd.Series([4, 'ETH', 1003, 2500, 2500, 'OPEN', 'LONG', 'ACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([5, 'ETH', 1005, 0, 2500, 'OPEN', 'LONG', 'ACTIVE'], index=self.idx), ignore_index=True)
        
        bt.set_positions(df)

        bt.close_reverse_position(signal='SHORT', currprice={'LTC': 800, 'BTC': 1003, 'ETH': 2000}, date=4)
        
        positions = bt.get_positions()
        
        assert(positions.iloc[6]['Coin'] == 'LTC')
        assert(positions.iloc[0]['Amount'] + positions.iloc[1]['Amount'] > positions.iloc[6]['Bankroll'])
        assert(positions.iloc[6]['Type'] == 'CLOSE')
        assert(positions.iloc[6]['Position'] == 'SHORT')
        assert(positions.iloc[6]['Status'] == 'INACTIVE')
        
        assert(positions.iloc[7]['Coin'] == 'BTC')
        assert(positions.iloc[7]['Bankroll'] - positions.iloc[6]['Bankroll'] > positions.iloc[2]['Amount'] + positions.iloc[3]['Amount'])
        assert(positions.iloc[7]['Type'] == 'CLOSE')
        assert(positions.iloc[7]['Position'] == 'SHORT')
        assert(positions.iloc[7]['Status'] == 'INACTIVE')
        
        assert(positions.iloc[8]['Coin'] == 'ETH')
        assert(positions.iloc[8]['Bankroll'] - positions.iloc[7]['Bankroll'] > positions.iloc[4]['Amount'] + positions.iloc[5]['Amount'])
        assert(positions.iloc[8]['Type'] == 'CLOSE')
        assert(positions.iloc[8]['Position'] == 'SHORT')
        assert(positions.iloc[8]['Status'] == 'INACTIVE')
        
        assert(int(positions.iloc[8]['Bankroll'] - positions.iloc[7]['Bankroll']) == int((5000/1004) *2000))
        
        #long and short dosen't take place at same time as reverse positions are always closed
        
        df = pd.DataFrame(columns=self.idx)
        
        df = df.append(pd.Series([2, 'BTC', 1001, 12500, 2500, 'OPEN', 'SHORT', 'ACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([3, 'BTC', 1000, 15000, 2500, 'OPEN', 'SHORT', 'ACTIVE'], index=self.idx), ignore_index=True)
        
        df = df.append(pd.Series([4, 'ETH', 1003, 17500, 2500, 'OPEN', 'SHORT', 'ACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([5, 'ETH', 1005, 20000, 2500, 'OPEN', 'SHORT', 'ACTIVE'], index=self.idx), ignore_index=True)
        
        bt.set_positions(df)

        bt.close_reverse_position(signal='LONG', currprice={'BTC': 800, 'ETH': 1050}, date=4)
        
        positions = bt.get_positions()
        
        assert(positions.iloc[4]['Coin'] == 'BTC')
        assert(positions.iloc[0]['Amount'] + positions.iloc[1]['Amount'] < positions.iloc[4]['Bankroll'])
        assert(positions.iloc[4]['Type'] == 'CLOSE')
        assert(positions.iloc[4]['Position'] == 'LONG')
        assert(positions.iloc[4]['Status'] == 'INACTIVE')
        
        assert(positions.iloc[5]['Coin'] == 'ETH')
        assert(positions.iloc[5]['Bankroll'] - positions.iloc[4]['Bankroll'] < positions.iloc[2]['Amount'] + positions.iloc[3]['Amount'])
        assert(positions.iloc[5]['Type'] == 'CLOSE')
        assert(positions.iloc[5]['Position'] == 'LONG')
        assert(positions.iloc[5]['Status'] == 'INACTIVE')
        
    def test_close_all_positions(self):
        '''
        It works in reverse positions too - when there is both long and short. But that dosen't happens. So this function 
        is like worthless for now. But keeping it as it will useful later
        
        '''
        bt = Backtester(self.bars, self.signals)
       
        
        df = pd.DataFrame(columns=self.idx)
        
        df = df.append(pd.Series([2, 'BTC', 1001, 12500, 2500, 'OPEN', 'SHORT', 'ACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([3, 'BTC', 1000, 15000, 2500, 'OPEN', 'SHORT', 'ACTIVE'], index=self.idx), ignore_index=True)
        
        df = df.append(pd.Series([4, 'ETH', 1003, 17500, 2500, 'OPEN', 'SHORT', 'ACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([5, 'ETH', 1005, 20000, 2500, 'OPEN', 'SHORT', 'ACTIVE'], index=self.idx), ignore_index=True)
        
        bt.set_positions(df)
        
        bt.close_all_positions(date=5, currprice={'LTC': 800, 'BTC': 800, 'ETH': 1050})
        positions = bt.get_positions()
        
        assert(positions.iloc[4]['Coin'] == 'BTC')
        assert(int(positions.iloc[4]['Bankroll'] - positions.iloc[1]['Bankroll']) == int(5000 - (5000/1000.5) * 800))
        assert(positions.iloc[4]['Type'] == 'CLOSE')
        assert(positions.iloc[4]['Position'] == 'LONG')
        assert(positions.iloc[4]['Status'] == 'INACTIVE')
        
        assert(positions.iloc[5]['Coin'] == 'ETH')
        assert(positions.iloc[5]['Bankroll'] - positions.iloc[4]['Bankroll'] < positions.iloc[2]['Amount'] + positions.iloc[3]['Amount'])
        assert(positions.iloc[5]['Type'] == 'CLOSE')
        assert(positions.iloc[5]['Position'] == 'LONG')
        assert(positions.iloc[5]['Status'] == 'INACTIVE')
        
        
        df = pd.DataFrame(columns=self.idx)
        
        df = df.append(pd.Series([0, 'LTC', 1001, 10500, 500, 'OPEN', 'LONG', 'ACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([1, 'LTC', 1000, 10000, 500, 'OPEN', 'LONG', 'ACTIVE'], index=self.idx), ignore_index=True)
        
        df = df.append(pd.Series([2, 'BTC', 1001, 7500, 2500, 'OPEN', 'LONG', 'ACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([3, 'BTC', 1000, 5000, 2500, 'OPEN', 'LONG', 'ACTIVE'], index=self.idx), ignore_index=True)
        
        df = df.append(pd.Series([4, 'ETH', 1003, 2500, 2500, 'OPEN', 'LONG', 'ACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([5, 'ETH', 1005, 0, 2500, 'OPEN', 'LONG', 'ACTIVE'], index=self.idx), ignore_index=True)
        
        bt.set_positions(df)
        
        bt.close_all_positions(date=5, currprice={'LTC': 800, 'BTC': 1003, 'ETH': 2000})
        positions = bt.get_positions()
        
        assert(positions.iloc[6]['Coin'] == 'LTC')
        assert(positions.iloc[0]['Amount'] + positions.iloc[1]['Amount'] > positions.iloc[6]['Bankroll'])
        assert(positions.iloc[6]['Type'] == 'CLOSE')
        assert(positions.iloc[6]['Position'] == 'SHORT')
        assert(positions.iloc[6]['Status'] == 'INACTIVE')
        
        assert(positions.iloc[7]['Coin'] == 'BTC')
        assert(positions.iloc[7]['Bankroll'] - positions.iloc[6]['Bankroll'] > positions.iloc[2]['Amount'] + positions.iloc[3]['Amount'])
        assert(positions.iloc[7]['Type'] == 'CLOSE')
        assert(positions.iloc[7]['Position'] == 'SHORT')
        assert(positions.iloc[7]['Status'] == 'INACTIVE')
        
        assert(positions.iloc[8]['Coin'] == 'ETH')
        assert(positions.iloc[8]['Bankroll'] - positions.iloc[7]['Bankroll'] > positions.iloc[4]['Amount'] + positions.iloc[5]['Amount'])
        assert(positions.iloc[8]['Type'] == 'CLOSE')
        assert(positions.iloc[8]['Position'] == 'SHORT')
        assert(positions.iloc[8]['Status'] == 'INACTIVE')
        
        
        #the code also works with both long and short position but that dosen't happens so no test written for it
        
    def test_perform_trade(self):
        bt = Backtester(self.bars, self.signals, bankroll=20000)

        #date, coin, price, amount, tradetype, postion
        bt.perform_trade(1, 'BTC', {'BTC': 1000}, 2000, 'OPEN', 'LONG')
        bt.perform_trade(2, 'BTC', {'BTC': 1005}, 3000, 'OPEN', 'LONG')
        positions = bt.get_positions()
        
        assert(positions.iloc[0]['Coin'] == 'BTC')
        assert(positions.iloc[0]['Amount'] == 2000)
        assert(positions.iloc[0]['Position'] == 'LONG')
        assert(positions.iloc[0]['Bankroll'] == 18000)
        assert(positions.iloc[0]['Status'] == 'ACTIVE')

        assert(positions.iloc[1]['Coin'] == 'BTC')
        assert(positions.iloc[1]['Amount'] == 3000)
        assert(positions.iloc[1]['Position'] == 'LONG')
        assert(positions.iloc[1]['Bankroll'] == 15000)
        assert(positions.iloc[1]['Status'] == 'ACTIVE')
        
        df = pd.DataFrame(columns=self.idx)
        
        df = df.append(pd.Series([0, 'LTC', 1001, 10500, 500, 'OPEN', 'LONG', 'ACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([1, 'LTC', 1000, 10000, 500, 'OPEN', 'LONG', 'ACTIVE'], index=self.idx), ignore_index=True)
        
        bt.set_positions(df)
        
        bt.perform_trade(1, 'BTC', {'BTC': 1000, 'LTC': 1005}, 2000, 'OPEN', 'SHORT')
        
        positions = bt.get_positions()
        
        assert(positions.iloc[0]['Status'] == 'INACTIVE')
        assert(positions.iloc[1]['Status'] == 'INACTIVE')

        assert(positions.iloc[2]['Coin'] == 'LTC')
        assert(positions.iloc[2]['Bankroll'] > positions.iloc[1]['Bankroll'] + positions.iloc[1]['Amount'] + positions.iloc[0]['Amount'])
        assert(positions.iloc[2]['Type'] == 'CLOSE')
        assert(positions.iloc[2]['Position'] == 'SHORT')
        assert(positions.iloc[2]['Status'] == 'INACTIVE')
        
        assert(positions.iloc[3]['Type'] == 'OPEN')
        assert(positions.iloc[3]['Position'] == 'SHORT')
        assert(positions.iloc[3]['Status'] == 'ACTIVE')
        

        assert(int(positions.iloc[3]['Bankroll']) == int(positions.iloc[2]['Bankroll'] + positions.iloc[3]['Amount']))
        
        #Asserts For shorts open and opening long. 
        df = pd.DataFrame(columns=self.idx)
        
        df = df.append(pd.Series([0, 'LTC', 1001, 10500, 500, 'OPEN', 'SHORT', 'ACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([1, 'LTC', 1000, 11000, 500, 'OPEN', 'SHORT', 'ACTIVE'], index=self.idx), ignore_index=True)
        
        bt.set_positions(df)
        
        bt.perform_trade(1, 'BTC', {'BTC': 1000, 'LTC': 1005}, 2000, 'OPEN', 'LONG')
        
        positions = bt.get_positions()
        
        assert(positions.iloc[0]['Status'] == 'INACTIVE')
        assert(positions.iloc[1]['Status'] == 'INACTIVE')
        assert(positions.iloc[2]['Status'] == 'INACTIVE')

        assert(int(positions.iloc[2]['Bankroll'] - (positions.iloc[0]['Bankroll'] - positions.iloc[0]['Amount'])) == int(1000 - (1000/1000.5) * 1005))
        assert(int(positions.iloc[2]['Bankroll'] - positions.iloc[3]['Bankroll']) == int(positions.iloc[3]['Amount']))
        
        #When there are inactive values
        df = pd.DataFrame(columns=self.idx)
        
        df = df.append(pd.Series([0, 'LTC', 1001, 10500, 500, 'OPEN', 'SHORT', 'INACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([0, 'LTC', 1001, 10000, 500, 'CLOSE', 'LONG', 'INACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([0, 'LTC', 1001, 10500, 500, 'OPEN', 'SHORT', 'ACTIVE'], index=self.idx), ignore_index=True)
        df = df.append(pd.Series([1, 'LTC', 1000, 11000, 500, 'OPEN', 'SHORT', 'ACTIVE'], index=self.idx), ignore_index=True)
        
        bt.set_positions(df)
        
        bt.perform_trade(1, 'BTC', {'BTC': 1000, 'LTC': 1005}, 2000, 'OPEN', 'LONG')
        
        positions = bt.get_positions()
        
        assert(positions.iloc[0]['Status'] == 'INACTIVE')
        assert(positions.iloc[1]['Status'] == 'INACTIVE')
        assert(positions.iloc[2]['Status'] == 'INACTIVE')
        assert(positions.iloc[3]['Status'] == 'INACTIVE')
        
        assert(int(positions.iloc[4]['Bankroll'] - (positions.iloc[2]['Bankroll'] - positions.iloc[2]['Amount'])) == int(1000 - (1000/1000.5) * 1005))
        assert(int(positions.iloc[4]['Bankroll'] - positions.iloc[5]['Bankroll']) == int(positions.iloc[5]['Amount']))
        
        
    def test_find_best(self):
        bt = Backtester(self.bars, self.signals)
        indicators = bt.find_best()
        
        #print(indicators)
        
        assert(indicators[0]['coin'] == 'BTC') #0.04917342 of btc is smaller than 0.05737299 of eth
        assert(indicators[0]['position'] == 'SHORT')
        
        assert(indicators[1]['coin'] == 'BTC') #0.71055381 of btc is better than 0.47474463 of eth
        assert(indicators[1]['position'] == 'LONG')
        
        assert(indicators[2]['coin'] == 'ETH') #0.72495607 of eth is better than 0.47894477 of btc
        assert(indicators[2]['position'] == 'LONG')
        
        assert(indicators[3]['coin'] == 'BTC') #0.26658264 of btc is smaller than 0.28919481 of eth
        assert(indicators[3]['position'] == 'SHORT')
        
        assert(indicators[9]['coin'] == 'BTC') #0.87507216 of btc is bigger than 0.80857246 of eth
        assert(indicators[9]['position'] == 'LONG')
        
    def test_perform_backtest(self):

        
        bt = Backtester(self.bars, self.signals, comission=0.1)
        bt.perform_backtest()
        positions = bt.get_positions()
        portfolioValue = bt.get_portfolioValue()
        
        assert(positions.iloc[0]['Position'] == 'SHORT')
        assert(positions.iloc[0]['Type'] == 'OPEN')
        assert(positions.iloc[1]['Type'] == 'CLOSE')
        assert(positions.iloc[1]['Position'] == 'LONG')
        
        if positions.iloc[0]['Price'] < positions.iloc[1]['Price']:
            assert(positions.iloc[0]['Bankroll'] - positions.iloc[0]['Amount'] > positions.iloc[1]['Bankroll'])
            
        #no tests for short