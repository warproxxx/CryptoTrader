# Crypto Scraper

![Download Data](https://i.imgur.com/hiSbDgG.png)

I was backtesting some trading strategy for my academic dissertation and needed hourly bitcoin data from 2013. 

I didn't found a good solution so i made this script to scrap data from Bitfinex. 

**Usage:**

First import the BtcFinex class to get Bitcoin data from Bitfinex

    from CryptoScraper import BtcFinex

Create a instance and download data if this in the first run. The repository already contains hourly data till March 2018. You can make changes to url variable in bitfinex.py to grab data from a different timeframe. If you do so, make sure you clear the cache folder before.

    finex = BtcFinex()
	finex.loadData()

Note that Bitfinex API limits total requests to 10 per minute so the program might take some break.

After downloading, call getCleanData() function to get a pandas dataframe of the data. Forward fill is done in places where the Bitfinex API do not return any data. The csv files are located in cache folder. final-rough.csv contains data without forward fill and final-clean.csv contains data with forward fill before being read as a pandas dataframe.

    df = finex.getCleanData()

Optionally, set Time column as the index. It is in UNIX Timestamp format.

    df.set_index('Time', inplace=True)

![Pandas Dataframe of data](https://i.imgur.com/ZXObhE4.png)