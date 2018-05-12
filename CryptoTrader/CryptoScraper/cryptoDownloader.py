import datetime
import calendar
import requests
import pandas as pd
import json
import os.path
import time
import datetime
import CryptoScraper

class getAllData:
    
    '''
    Returns all data in a dictionary
    '''
    
    def __init__(self, cacheOnly, coins=['BTC', 'DASH', 'DOGE', 'ETH', 'LTC', 'STR', 'XMR', 'XRP'], how='intersect', customTimeframe = {'start': '1990-01-01', 'end': '2050-01-01'}):
        '''
        cacheOnly: true or false.
        Returns data from cache only
        
        how: 'intersect' and 'union'. Union appends zero. Note that in union smallestEnding is used.
        
        timerange: dictionary containing start and end time. 
        Format: %Y-%m-%d
        
        '''
        self.how = how
        self.cache = cacheOnly
        self.coins = coins
        self.customTimeframe = customTimeframe
        
    def data(self):
        coinDf = {}
        
        for coin in self.coins:
            print('Getting {} data'.format(coin))
            
            
            if (self.cache == False):
                crypto = cryptoDownloader(coin)
                crypto.download()
                
            coinDf[coin] = pd.read_csv(os.path.dirname(CryptoScraper.__file__) + '\cache\{}.csv'.format(coin))
            
        smallestStart = 9999999999
        largestStart = 0
        smallestEnd = 9999999999
        largestEnd = 0
        
        if (self.how == 'intersect' or self.how == 'union'):

            for key in coinDf:
                startingDate = coinDf[key].iloc[0]['Date']
                endingDate = coinDf[key].iloc[-1]['Date']
                
                if (startingDate < smallestStart):
                    smallestStart = startingDate
                    
                if (startingDate > largestStart):
                    largestStart = startingDate
                    
                if (endingDate < smallestEnd):
                    smallestEnd = endingDate
                    
                if (endingDate > largestEnd):
                    largestEnd = endingDate
        
        if (self.how == 'intersect'):

            for key in coinDf:
                coinDf[key] = coinDf[key][coinDf[key]['Date'] >= largestStart]
                coinDf[key] = coinDf[key][coinDf[key]['Date'] <= smallestEnd]

        else:

            # print(smallestStart)
            # print(largestStart)
            # print(smallestEnd)
            # print(largestEnd)

            for key in coinDf:
                dates = pd.DataFrame([x for x in range(int(smallestStart), int(smallestEnd), 3600)]) #in union smallestEnding is used
                dates.columns = ['Date']
                
                coinDf[key].set_index('Date', inplace=True)
                dates.set_index('Date', inplace=True)
                
                full_data = pd.concat([coinDf[key], dates], axis=1).fillna(value=0)
                full_data = full_data.reset_index()

                coinDf[key] = full_data
        
        #now custom timeframe
        startFrame = int(time.mktime(datetime.datetime.strptime(self.customTimeframe['start'], "%Y-%m-%d").timetuple()))
        endFrame = int(time.mktime(datetime.datetime.strptime(self.customTimeframe['end'], "%Y-%m-%d").timetuple()))

        for key in coinDf:
            coinDf[key] = coinDf[key][coinDf[key]['Date'] >= startFrame]
            coinDf[key] = coinDf[key][coinDf[key]['Date'] <= endFrame]

            coinDf[key] = coinDf[key].reset_index(drop=True)

        return coinDf

class cryptoDownloader:

    '''
    Downloads 10 minute data from Poloniex and Bitfinex.    
    '''
    
    def __init__(self, symbol):
        self.poloniexURL = 'https://poloniex.com/public?command=returnChartData&currencyPair=BTC_{}&start={}&end=9999999999&period={}'
        self.bitfinexURL = 'https://api.bitfinex.com/v2/candles/trade:1h:tBTCUSD/hist?start={}&end={}&limit=1000'
        
        if (symbol == 'BTC'):
            self.cachefile = os.path.dirname(CryptoScraper.__file__) + '\cache\{}-downloading.csv'.format(symbol)
        else:
            self.cachefile = os.path.dirname(CryptoScraper.__file__) + '\cache\{}.csv'.format(symbol)
        
        self.symbol = symbol
        
        if (os.path.isfile(self.cachefile)): #if the file already exists start from the latest date
            time = str(int(pd.read_csv(self.cachefile).iloc[-1][0]))
            
            if (len(time) > 11):
                time = time[:-3]
            
            self.startdate = int(time) #read the last timestamp for csv file.
            self.startdate = self.startdate + 3600
        else:
            if (symbol == "BTC"):
                self.startdate = datetime.datetime.strptime('01/04/2013', '%d/%m/%Y') #Start collecting from April 1, 2013
            else:
                try:
                    firstRes = requests.get(self.poloniexURL.format(self.symbol, '0', '86400'))
                    firstData = firstRes.text
                    firstDf = pd.read_json(firstData, convert_dates=False)
                    self.startdate = firstDf['date'][0]
                    
                    btc = pd.read_csv(os.path.dirname(CryptoScraper.__file__) + '\cache\BTC.csv')
                    closest = btc.iloc[(btc['Date']-self.startdate).abs().argsort()[0]]['Date']
                    
                    self.startdate = closest
                except:
                    print('Poloniex is blocking your request. Try using a VPN')
                
    def download(self):
        if (self.symbol == 'BTC'):
            self.bitcoinDownloader()
        else:
            btc = cryptoDownloader('BTC')
            btc.bitcoinDownloader()
            
            self.poloniexDownloader()

    def bitcoinDownloader(self):
    
        if (isinstance(self.startdate, int)):
            start_unixtime = self.startdate
        else:
            start_unixtime = calendar.timegm(self.startdate.utctimetuple())
            
            
        latest_time = int(time.time() - 60 * 60 * 24) #The real ending time. Collect data from starttime to current time - 24 hours
        
        track_time = time.time() #because bitstamp only allows 10 requests per minute. Take rest if we are faster than that
        count = 0
        
        
        if (os.path.isfile(self.cachefile)):
            allDf = pd.read_csv(self.cachefile)
        else:
            allDf = pd.DataFrame(columns=['Date', 'Open', 'Close', 'High', 'Low', 'Volume'])
        
        

        while (start_unixtime < latest_time):
            end_unixtime = start_unixtime + 60*60*24*30 #30 days at a time

            if (end_unixtime > latest_time):
                end_unixtime = latest_time #if the time is in future.

            url = 'https://api.bitfinex.com/v2/candles/trade:1h:tBTCUSD/hist?start={}&end={}&limit=1000'.format(str(start_unixtime) + "000", str(end_unixtime) + "000") #1 hour can be changed to any timeframe
            response = requests.get(url)
            data = response.json()

            df = pd.DataFrame(data).sort_values(by=0).reset_index(drop=True) #set the date column as index and sort all data
            
            df.columns = ['Date', 'Open', 'Close', 'High', 'Low', 'Volume']
            
            allDf = allDf.append(df)
            allDf.to_csv(self.cachefile, index=None)

            print('Saved till {}'.format(datetime.datetime.fromtimestamp(int(end_unixtime)).strftime('%Y-%m-%d %H:%M:%S')))

            start_unixtime = end_unixtime
            count = count + 1

            if (count == 10): #if 10 requests are made
                count = 0 #reset it

                diff = time.time() - track_time

                if (diff <= 60):
                    print('Sleeping for {} seconds'.format(str(60 - diff)))
                    time.sleep(60 - diff) #sleep


                track_time = time.time()
                
        cleanedData = self.cleanData(allDf)
        cleanedData.to_csv(self.cachefile.replace('-downloading', ''))
        
    def poloniexDownloader(self):
        
        res = requests.get(self.poloniexURL.format(self.symbol, int(self.startdate), 1800))
        data = res.text
        df = pd.read_json(data, convert_dates=False)
        df = df[['date', 'open', 'close', 'high', 'low', 'volume']]
        df.columns = ['Date', 'Open', 'Close', 'High', 'Low', 'Volume']
        
        
        df = df[df['Date'] != 0] #keeping non zeros only
        
        if (df.shape[0] >= 1): #becase might be empty sometimes        
            if ([df['Date']%3600][0][0] != 0): #because keeping 2 values
                df = df[1:]

            df = df.reset_index(drop=True)

            df = self.mergePoloniexData(df)

            if (os.path.isfile(self.cachefile)):
                df.to_csv(self.cachefile, mode='a', header=False, index=None)
            else:
                df.to_csv(self.cachefile, index=None)
        
    def mergePoloniexData(self, df, time=2):
        retDf = pd.DataFrame(columns=['Date', 'Open', 'Close', 'High', 'Low', 'Volume'])
        
        for i in range(0, df.shape[0], time):

            tempdf = df.iloc[i:i+time]
            retDf = retDf.append({'Date': tempdf.iloc[0]['Date'], 'Open': tempdf.iloc[0]['Open'], 'Close': tempdf.iloc[-1]['Close'], 'High': max(tempdf['High']), 'Low': min(tempdf['Low']), 'Volume': sum(tempdf['Volume'])}, ignore_index=True)
        
        retDf['Date'] = retDf['Date'].astype(int)
        
        return retDf
         
    
    def cleanData(self, df):
        '''
        Cleans the data. Remove 3 extra 0 if needed. Else makes sure all data is avilable by forward filling        
        '''
        
        dates = pd.DataFrame([x for x in range(int(df.iloc[0]['Date']), int(df.iloc[-1]['Date']), 3600000)])
        dates.columns = ['Date']
        df.set_index('Date', inplace=True)
        dates.set_index('Date', inplace=True)
        
        df.drop_duplicates(inplace=True)
        full_data = pd.concat([df, dates], axis=1).fillna(method='ffill')
        
        if (len(str(full_data.index[0])) > 11):
            full_data.index = [str(x)[:-3] for x in full_data.index]
        
        full_data.index.name = 'Date'
        
        abc = pd.Series(full_data.index)
        difference =abc.astype(int) - abc.shift(1).fillna(method ='bfill').astype(int)
        assert(sum(difference != 3600.0) == 1)
        return full_data