from data_utils import PriceFunctions
import numpy as np
import pandas as pd
        
class TestPriceFunctions():   

    def setup_method(self, test_method):
        self.pf = PriceFunctions()
        self.coins = ['BTC', 'ETH', 'DASH', 'DOGE', 'LTC', 'STR', 'XMR', 'XRP']