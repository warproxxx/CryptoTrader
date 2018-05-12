# Technical Analysis

Performs time merge/split and MACD, RSI, Bollinger Band, On Balance Volume and Volume Change Technical Analysis on given pandas dataframe for a given timeframe and period and returns it in dictonary (data for different timeframes) or a dataframe.

**Usage:**

First import the TechnicalAnalysis class

    from TechnicalAnalysis import TechnicalAnalysis

Create an instance using pandas dataframe of stock data. The data should contain: Open, Close, High, Low, Volume and Classification

The values in timeframe refer to times that should be merged. Value of 3 and 6 means each 3 and 6 datas will be merged in which Technical Analysis will be done

The values in period refer to Technical Indicator Period. The value should be greater than 3. 14 and 20 days are common periods.

    ta = TechnicalAnalysis(df, timeframe=[3,6,12,24], period=[14, 20])

The above line performs 3 hour, 6 hour, 12 hour and daily Technical Analysis on a period of 14 and 20.

Run the merge_time method to merge different timeframes.
    
	ta.merge_time()

Call the perform method with the name of analysis
	
	ta.perform('macd')
    ta.perform('bollingerband')
    ta.perform('volumechange')
    ta.perform('rsi')
    ta.perform('obv')

Get the dataframe
	
	df = ta.get_dataframe()

Or optionally get the dictionary with different timeframe as keys

	dic = ta.get_dic()

![Getting TA data](https://i.imgur.com/kGMGMhd.png)