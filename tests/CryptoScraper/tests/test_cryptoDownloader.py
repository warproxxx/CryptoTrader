import pandas as pd

from CryptoScraper import cryptoDownloader

class TestcryptoDownloader:
    
    def test_download(self):
        '''
        Tests all functionality as a whole
        '''
        try:
            cd = cryptoDownloader('LTC')
            cd.download()          
        except:
            print('Poloniex might be blocking your requests');
            
            
        #read file. Asssert size  
        btc = pd.read_csv('CryptoScraper/cache/BTC.csv');
        ltc = pd.read_csv('CryptoScraper/cache/LTC.csv');
        dash = pd.read_csv('CryptoScraper/cache/DASH.csv');
        doge = pd.read_csv('CryptoScraper/cache/DOGE.csv');
        eth = pd.read_csv('CryptoScraper/cache/ETH.csv');
        str = pd.read_csv('CryptoScraper/cache/STR.csv');
        xmr = pd.read_csv('CryptoScraper/cache/XMR.csv');
        xrp = pd.read_csv('CryptoScraper/cache/XRP.csv');
        
        diff = btc['Date'] - btc.shift(1)['Date'].fillna(method ='bfill').astype(int)       
        assert(sum(diff != 3600.0) == 1)
        
        diff2 = ltc['Date'] - ltc.shift(1)['Date'].fillna(method ='bfill').astype(int)       
        assert(sum(diff2 != 3600.0) == 1)
        
        diff3 = dash['Date'] - dash.shift(1)['Date'].fillna(method ='bfill').astype(int)       
        assert(sum(diff3 != 3600.0) == 1)
        
        diff4 = doge['Date'] - doge.shift(1)['Date'].fillna(method ='bfill').astype(int)       
        assert(sum(diff4 != 3600.0) == 1)
        
        diff5 = eth['Date'] - eth.shift(1)['Date'].fillna(method ='bfill').astype(int)       
        assert(sum(diff5 != 3600.0) == 1)
        
        diff6 = str['Date'] - str.shift(1)['Date'].fillna(method ='bfill').astype(int)       
        assert(sum(diff6 != 3600.0) == 1)
        
        diff7 = xmr['Date'] - xmr.shift(1)['Date'].fillna(method ='bfill').astype(int)       
        assert(sum(diff7 != 3600.0) == 1)
        
        diff8 = xrp['Date'] - xrp.shift(1)['Date'].fillna(method ='bfill').astype(int)       
        assert(sum(diff8 != 3600.0) == 1)