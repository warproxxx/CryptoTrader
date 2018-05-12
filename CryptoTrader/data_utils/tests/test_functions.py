from data_utils import BasicFunctions, PriceFunctions
import numpy as np
import pandas as pd

class TestBasicFunctions():
    def test_initialize_mini_batch(self):
        bf = BasicFunctions()
        
        np.random.seed(1)
        X = np.random.randn(12288, 148)
        y = np.random.randn(1, 148)

        batches = bf.initialize_mini_batch(X,y,64)
        assert(batches[0][0].shape == (12288, 64)) #testing X
        assert(batches[1][0].shape == (12288, 64))
        assert(batches[2][0].shape == (12288, 20))
        assert(batches[0][1].shape == (1, 64)) #testing y
        assert(batches[1][1].shape == (1, 64))
        assert(batches[2][1].shape == (1, 20))
        
class TestPriceFunctions():   

    def setup_method(self, test_method):
        self.pf = PriceFunctions()
        self.coins = ['BTC', 'ETH', 'DASH', 'DOGE', 'LTC', 'STR', 'XMR', 'XRP']


    def test_to_same_starting(self):
        self.coins = ['BTC', 'ETH', 'DASH', 'DOGE', 'LTC', 'STR', 'XMR', 'XRP']
        
        dfs = {}
        
        for coin in self.coins:
            dfs[coin] = self.pf.get_pandas(coin=coin, targetdays=24, absolute=True)

        dfs = self.pf.to_same_starting(dfs)
        
        assert(sum(dfs['BTC'].index != dfs['ETH'].index) == 0)
        assert(sum(dfs['ETH'].index != dfs['DASH'].index) == 0)
        assert(sum(dfs['DASH'].index != dfs['DOGE'].index) == 0)
        assert(sum(dfs['DOGE'].index != dfs['LTC'].index) == 0)
        assert(sum(dfs['LTC'].index != dfs['STR'].index) == 0)
        assert(sum(dfs['STR'].index != dfs['XMR'].index) == 0)
        assert(sum(dfs['XMR'].index != dfs['XRP'].index) == 0)

    def test_get_pandas(self):

        for coin in self.coins:
            df = PriceFunctions().get_pandas(coin=coin, targetdays=24)
            assert(sum(df.index[1:] - df.index[:-1] != 3600) == 0)
            assert({'Open', 'Open', 'High', 'Low', 'Volume', 'Percentage Change', 'Classification'}.issubset(df.columns))