import pandas as pd
import json
import matplotlib.pyplot as plt
from BackTest.calculations import Calculations
import datetime
import matplotlib
import matplotlib.dates as mdates

class Backtester:

    '''
    Backtesting module that does everything

    At the end, in positions, a new column - current net worth should be added
    '''
    
    #add margin rates and margin size too later
    def __init__(self, bars, signals, period=1, bankroll=10000, stake=1000, comission=0, slippage=0, maxper=1):
        '''
        Parameters:
        ___________
        bars (dictionary):
        Dictionary of Pandas dataframe containing Open, Close, High and Low Value. The Close value will be used
        
        signals (dictionary):
        Dictionary of coins that contain Numpy array containg direction probablity and magnitude of change.
        
        period (int):
        Number that represents how far in the future the timeframe lies
        1 is used for classification whose target is 1 timeframe away and so on
        
        bankroll (int optional):
        The initial cash to start with
        
        stake (int optional):
        size of each trade
        
        comission (int optional):
        Comission per trade in percentage (out of 100)
        
        slippage (int optional):
        Slippage per trade in percentage (out of 100)

        maxper (int optional):
        Maximum allocated in a trade if probablity is great
        '''
        self.bars = bars
        self.signals = signals
        self.period = period
        self.bankroll = bankroll
        self.stake = stake
        self.comission = comission
        self.slippage = slippage
        self.maxper = maxper

        #Type has open or close. Position has long or short. So 
        #long close means closing short
        #long open mean opening long
        #short open meaning opening short
        #short close meaning closing short 
        self.positions = pd.DataFrame(columns=['Date', 'Coin', 'Price', 'Bankroll', 'Amount', 'Type', 'Position', 'Status'])
        self.allValues = [] #all values in find best
        self.portfolioValue = pd.DataFrame(columns=['Date', 'Value'])
        self.perform_assertion()
        self.wentZero = 0 #to track if ever went to zero
        
    
    def perform_assertion(self):
        '''
        Check if all the values have same timeframes and if they have all required columns
        '''
        shape = self.bars[list(self.bars)[0]].shape
        
        keyList=sorted(self.bars.keys())
        
        for i, key in enumerate(keyList):
            if i > 0:
                #self.bars[keyList[i]]['Date'] = pd.to_datetime(self.bars[keyList[i]]['Date']) #converting to pandas date if they are not like that
                
                try:
                    assert(self.bars[keyList[i]]['Date'].equals(self.bars[keyList[i-1]]['Date']))
                    
                except AssertionError:
                    print("The dates in your dataframe do not match. The dates of {} and {} are different at {}".format(keyList[i], keyList[i-1], AssertionError))
                
                try:
                    assert(self.signals[keyList[i]].shape == self.signals[keyList[i-1]].shape)
                except AssertionError:
                    print("The signals don't match at {} and {}".format(keyList[i], keyList[i-1]))
    
    def set_positions(self, df):
        self.positions = df
    
    def get_positions(self):
        return self.positions

    def get_allValues(self):
        return self.allValues
        
    def get_avilableamount(self):
        '''
        Checks the dataframe and finds how much percentage is tradable

        Returns:
        ________
        The percentage that is avilable to trade
        '''
        
        avilable = {}

        if (self.positions.shape[0] == 0):
            currBankroll = self.bankroll
            dfsum = 0
        else:
            currBankroll = self.positions['Bankroll'].iloc[-1]
            activePositions = self.positions[self.positions['Status'] == 'ACTIVE']
 
            tempdf = activePositions.apply(lambda x: (x['Amount']/x['Price']) * -1 if x['Position'] == 'SHORT' else (x['Amount']/x['Price']), axis=1) #x['Amount']/x['Price'] to get value in coin.
            
            
            if (tempdf.shape[0] == 0):
                dfsum =0
            else:
                dfsum = sum(tempdf) * activePositions['Price'].iloc[-1]

        totalValue = currBankroll + dfsum #change should be made to dfsum to get current close price and calculate the worth.
        
        avilable['long'] = currBankroll
        avilable['short'] = totalValue * 2 - avilable['long']

        if (avilable['short'] < 0):
            avilable['short'] = 0
        
        if (avilable['long'] < 0):
            avilable['long'] = 0

        #print("dfsum: {} Avilable: {} Total Value: {}".format(dfsum, avilable, totalValue)) #the new change in value calculation has caused issue in short

        return avilable, totalValue
        
    def get_portfolioValue(self):
        return self.portfolioValue

    def check_validity(self, position, size, date=''):
        '''
        Check if a long or short position can be opened currently.
        
        Returns:
        ________
        True if perforamble
        
        The size of long and short that can be performed if not performable
        '''
        
        avilable,totalValue = self.get_avilableamount()

        returnVals = {}

        if (totalValue < 0): #forced liquidation
            self.wentZero = 1
            
        if (self.wentZero == 1):
            totalValue = 0 #can remove it temporarily
            
        self.portfolioValue = self.portfolioValue.append({'Date': date, 'Value': totalValue}, ignore_index=True)
        


        if position == 'LONG':
            if (avilable['long'] >= size):
                returnVals['boolean'] = True
            else:
                returnVals['boolean'] = False
                returnVals['avilable'] = avilable['long'] 
            
        elif position == 'SHORT':
            if (avilable['short'] >= size):
                returnVals['boolean'] = True
            else:
                returnVals['boolean'] = False
                returnVals['avilable'] = avilable['short'] 

        return returnVals
    
    def get_currentWorth(self):
        '''
        Evaluates net worth from positions that are currently open
        '''
        activePositions = self.positions[self.positions['Status'] == 'ACTIVE']
        tempdf = activePositions.apply(lambda x: x['Amount'] * -1 if x['Position'] == 'SHORT' else x['Amount'], axis=1)
        print(self.positions)

    def close_reverse_position(self, signal, currprice, date):
        ''' 
        Close all reverse positions. If long signal is generated and short position is open, close it and vice versa
        
        Parameters:
        ___________

        signal: (string)
        'LONG' or 'SHORT'

        currprice: (dict)
        dictionary containing symbols and their price while closing position

        date: (int)
        Date in which the trade takes place
        '''
        
        #perform reverse trade
        #call perform_trade function to perform the reverse trade and change status to inactive
        if (signal == 'LONG'):
            reverse = 'SHORT'
        elif (signal == 'SHORT'):
            reverse = 'LONG'
            
        
        closingsignals = self.positions[(self.positions['Status'] == 'ACTIVE') & (self.positions['Position'] == reverse)]
        
        if (self.positions.shape[0] == 0):
            oldBankroll = self.bankroll
        else:
            oldBankroll = self.positions['Bankroll'].iloc[-1]

        #now for given coin close at the current price
        for coin in currprice:
            requiredcoins = closingsignals[self.positions['Coin'] == coin]

            if(closingsignals[self.positions['Coin'] == coin].shape[0] != 0): #this also happens automatically with the other warning
                perChange = (currprice[coin] - requiredcoins['Price'])/requiredcoins['Price']
                
                if (reverse == 'LONG'):
                    newAmounts = requiredcoins['Amount'] + requiredcoins['Amount'] * perChange
                elif (reverse == 'SHORT'):
                    requiredcoins['Amount'] = requiredcoins['Amount'] * -1
                    newAmounts = requiredcoins['Amount'] + requiredcoins['Amount'] * perChange

                amount = sum(requiredcoins['Amount'])
                closingChange = sum(newAmounts) - ((self.comission/100) * abs(amount))
                

                newData = pd.Series({'Date': date, 'Coin': coin, 'Price': currprice[coin], 'Bankroll': oldBankroll+closingChange, 'Amount': abs(amount), 'Type': 'CLOSE', 'Position': signal, 'Status': 'INACTIVE'})
                #also change old ones to inactive. Append newData too on the dataframe at end. And works for long. also check for short
                self.positions = self.positions.append(newData, ignore_index=True)
                oldBankroll = oldBankroll+closingChange

        self.positions.loc[(self.positions['Status'] == 'ACTIVE') & (self.positions['Position'] == reverse), 'Status'] = 'INACTIVE'


    def close_all_positions(self, date, currprice):
        '''
        Just call the close reverse position twice
        '''
        #I think getting the coin names is not required

        self.close_reverse_position('LONG', currprice, date)
        self.close_reverse_position('SHORT', currprice, date)

    def perform_trade(self, date, coin, currprice, amount, tradetype, position):
        '''
        Perform trade and change dataframe to reflect it
        
        Parameters:
        ___________
        
        Date: (int)
        The date in which the trade took place
        
        coin (3 words):
        Symbol like btc
        
        currprice: (dict)
        dictionary containing symbols and their price
        
        amount: (int)
        In money, how many's to open
        
        tradetype: (string)
        Open or Close
        
        
        postion: (string)
        LONG or SHORT
        '''
        
        #Change dataframe that way
        #The trade data should be added to self.positions.
        #The initial bankroll value should be derived from the variable
        #after that from previous +- trade
        #bankroll currently contains new value after position is opened

        self.close_reverse_position(position, currprice, date) #Close reverse positions before performing

        if (self.positions.shape[0] == 0):
            curbankroll = self.bankroll
        else:
            curbankroll = self.positions['Bankroll'].iloc[-1]

        amount = amount - ((self.comission/100) * abs(amount))

        if position == 'LONG':
            newbankroll = curbankroll-amount
        elif position == 'SHORT':
            newbankroll = curbankroll+amount

        ser = pd.Series({'Date': date, 'Coin': coin, 'Price': currprice[coin], 'Bankroll': newbankroll, 'Amount': abs(amount), 'Type': tradetype, 'Position': position, 'Status': 'ACTIVE'})
        
        self.positions = self.positions.append(ser, ignore_index=True)
    
    def find_best(self):
        '''
        Finds the best coin to buy for that day
        '''
        
        #compare the x of the 3            
        #The one with highet probablity is chosen
        
        shape = len(self.bars[list(self.signals)[0]])
        keyList=sorted(self.signals.keys())
        bests = []
        
        best = {'probablitynorm': 0}
        
        for i in range(shape): #loop through dataframe

            values = pd.DataFrame(columns=['coin', 'date', 'probablity', 'probablitynorm', 'percentage', 'position'])
            
            for idx, key in enumerate(keyList): #to loop through dict and compare values of different
                value = {}

                probablity = self.signals[key][i][0]
                
                if probablity < 0.5: #if i feel confused - it is working. I need the smaller number when its smaller and bigger when it is bigger
                    x = 1 - probablity
                else:
                    x = probablity
                    
                if x > best['probablitynorm']:
                    best['coin'] = key
                    best['date'] = self.bars[key]['Date'][i]
                    best['probablity'] = probablity
                    best['probablitynorm'] = x
                    best['percentage'] = self.signals[key][i][1]
                    
                    if (probablity < 0.5):
                        best['position'] = 'SHORT'
                    else:
                        best['position'] = 'LONG'
                    
                
                value['coin'] = key
                value['date'] = self.bars[key]['Date'][i]
                value['probablity'] = probablity
                value['probablitynorm'] = x
                value['percentage'] = self.signals[key][i][1]
                
                if (probablity < 0.5):
                    value['position'] = 'SHORT'
                else:
                    value['position'] = 'LONG'

                values = values.append(value, ignore_index=True)

            self.allValues.append(values)
            bests.append(best)
            best = {'probablitynorm': 0}
        
        return bests

    def perform_backtest(self):
        '''
        The main method in the file that calls other methods to backtest a given strategy.

        '''
        data = self.find_best()

        for i, dic in enumerate(data):
        
            avilable,totalValue = self.get_avilableamount()
            
            if (totalValue < 0):
                totalValue = 0 #change to 0 or not
            
                
            prob = dic['probablity']
            perc = dic['percentage']
            coin = dic['coin']
            date = dic['date']
            pos = dic['position']
            normprob = dic['probablitynorm']

            positionPercentage = 0

            if (normprob > 0.75 or perc > 0.007):
                positionPercentage = self.maxper
            elif (normprob > 0.65 or perc > 0.005):
                positionPercentage = self.maxper/2
            elif (normprob > 0.55 or perc > 0.002):
                positionPercentage = self.maxper/3.3

            currprice = {}

            for key in self.bars:
                currprice[key] = self.bars[key][self.bars[key]['Date'] == date].iloc[0]['Close']

            #print(self.allValues[i][self.allValues[i]['coin'] == coin]['position'])
            #if there is a active LONG in a given coin close in that coin only - possibly. This after - worth, chart, sharpe ration, drawdown.

            # if (pos == 'LONG'):
            #     oppositeVals = self.positions[self.positions['Status'] == 'ACTIVE' and self.positions['Postion'] == 'SHORT' and self.positions['Coin'] == coin]
            # elif (pos == 'SHORT'):
            #     oppositeVals = self.positions[self.positions['Status'] == 'ACTIVE' and self.positions['Postion'] == 'LONG' and self.positions['Coin'] == coin]

            if (positionPercentage !=0):
                self.close_reverse_position(pos, currprice, date) #Close reverse positions before opening new

                if (self.positions.shape[0] == 0):
                    currBankroll = self.bankroll
                else:
                    currBankroll = self.positions['Bankroll'].iloc[-1]

                posSize = int(positionPercentage * currBankroll)
                validity = self.check_validity(position=pos, size=posSize, date=date)

                if (validity['boolean'] == True):
                    self.perform_trade(date=date, coin=coin, currprice=currprice, amount=posSize, tradetype='OPEN', position=pos)
                else:
                    self.perform_trade(date=date, coin=coin, currprice=currprice, amount=validity['avilable'], tradetype='OPEN', position=pos)

            # if (oppositeVals.shape[0] >= 0):
            #     print('Reverse signal received')
            # elif (pos == 'LONG' and (self.positions['Status'] == 'ACTIVE' and self.positions.iloc[-1]['Position'] == 'SHORT'): #but it has to be that coin the signal is in.
            #     print('Manual Close Long')
            #     self.close_reverse_position(pos, currprice, date)
            # elif (pos == 'SHORT' and self.positions.iloc[-1]['Status'] == 'ACTIVE' and self.positions.iloc[-1]['Position'] == 'LONG'):
            #     print('Manual Close Short at {}'.format(date))
            #     self.close_reverse_position(pos, currprice, date)

        self.close_all_positions(date=date, currprice = currprice)

    def get_outcome(self):
        '''
        Calculates Sharpe Ratio, Shortino Ratio, Drawdown of portfolio strategy and individual assets
        
        Requirement:
        self.bars, self.position and self.portfolioValue should be defined. So backtest function most run beforehand
        '''
        fig, axes = plt.subplots(nrows=3)

        fig.set_figheight(18)
        fig.set_figwidth(10)

        self.portfolioValue['Date'] = [datetime.datetime.fromtimestamp(x) for x in self.portfolioValue['Date']]
        self.positions['Date'] = [datetime.datetime.fromtimestamp(x) for x in self.positions['Date']]

        axes[0].set_title('Portfolio Movement')


        axes[0].plot(self.portfolioValue['Date'], self.portfolioValue['Value'], label='Portfolio') 
        
        axes[1].set_title('Porfolio Change')
        axes[1].bar(self.portfolioValue['Date'], self.portfolioValue['Value'].pct_change())
        self.positions['Rough'] = self.positions.apply(lambda x: x['Amount'] * -1 if x['Position'] == 'SHORT' else x['Amount'], axis=1)
        
 
        axes[2].set_title('Portfolio Position')
        axes[2].bar(self.positions['Date'], self.positions['Rough'], width=0.05)

        self.positions.drop('Rough', axis=1, inplace=True)

        c = Calculations()
        sharpe = round(c.sharpe_ratio(self.portfolioValue['Value']), 3)
        calmar = round(c.calmar_ratio(self.portfolioValue['Value']), 3)
        sortino = round(c.sortino_ratio(self.portfolioValue['Value']), 3)
        drawDown = c.drawDown(self.portfolioValue['Value'])
        totalReturn = c.total_return(self.portfolioValue['Value'])

        print("Portfolio Stats:\nTotal Return: {}%".format(round(totalReturn, 2)))
        print("Sharpe Ratio: {} Calmar Ratio: {} Sortino Ratio: {} Maximum Drawdown: {}%".format(sharpe, calmar, sortino, round(drawDown, 2)))

        for coin in self.bars:

            self.bars[coin]['Value'] = self.bankroll
            self.bars[coin]['Value'] = self.bars[coin]['Value'].astype(float)
            change = ((self.bars[coin]['Close'] - self.bars[coin]['Close'][0])/self.bars[coin]['Close'][0]) + 1

            sharpe = round(c.sharpe_ratio(self.bars[coin]['Close']), 3)
            calmar = round(c.calmar_ratio(self.bars[coin]['Close']), 3)
            sortino = round(c.sortino_ratio(self.bars[coin]['Close']), 3)
            drawDown = round(c.drawDown(self.bars[coin]['Close']), 3)
            totalReturn = round(c.total_return(self.bars[coin]['Close']), 3)

            print("\n{} Portfolio:\nTotal Return: {}%".format(coin, round(totalReturn, 2)))
            print("Sharpe Ratio: {} Calmar Ratio: {} Sortino Ratio: {} Maximum Drawdown: {}%".format(sharpe, calmar, sortino, round(drawDown, 2)))


            self.bars[coin]['Value'] = self.bars[coin]['Value'] * change

            #self.bars[coin]['Date']
            axes[0].plot(self.portfolioValue['Date'], self.bars[coin]['Value'], label=coin)

        
        axes[0].legend(loc=2)