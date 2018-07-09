# Crypto Scraper

![Download Data](https://i.imgur.com/hiSbDgG.png)

I was backtesting some trading strategy for my academic dissertation and needed hourly bitcoin data from 2013. 

I didn't found a good solution so i made this script to scrap data from Bitfinex and Poloniex. 

**Usage:**

First import the downloader class

    from CryptoScraper import cryptoDownloader, getAllData

Create a instance and download data if this in the first run. After that you can use cached data or redownload. The repository already contains hourly data till March 2018. You can make changes to url variable in the py file to grab data from a different timeframe. If you do so, make sure you clear the cache folder before.

    dr = getAllData(how='intersect')
	coinDfcoinDf = dr.data()

By default it downloads data for the following coins:
['BTC', 'DASH', 'DOGE', 'ETH', 'LTC', 'STR', 'XMR', 'XRP']

It can be changed via coins parameter in getAllData.

If you use the intersect option, data across same timeframe will be provided for all coins (For eg: if ETH was added on 2016 and Bitcoin had data from 2015, only data from 2016 will be returned. If you use union option, all possible data will be returned). You can also specify start and end date via customTimeframe dictionary.

You can set cacheOnly to True to only return data from cache. If you set it to false, new data will be downloaded.

Note that Bitfinex API limits total requests to 10 per minute so the program might take some break.


![Pandas Dataframe of data](https://i.imgur.com/ZXObhE4.png)