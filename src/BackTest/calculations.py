import numpy as np
import pandas as pd


class Calculations:
 

    def sharpe_ratio(self, data):
        '''
        http://www.edge-fund.com/Lo02.pdf
        
        https://sixfigureinvesting.com/2013/09/daily-scaling-sharpe-sortino-excel/
        '''
        n = 365 ** 0.5 #365 trading days in crypto
        
        percentage = data.pct_change()[1:]
        sharpe = (np.average(percentage)/np.std(percentage)) * n
        return sharpe
    
    def sortino_ratio(self, data):
        '''
        The ratio that only considers downside volatility
        '''
        n = 365 ** 0.5 #365 trading days in crypto
        df = pd.DataFrame(columns=['Portfolio', 'Percentage Change'])
        df['Portfolio'] = data
        df['Percentage Change'] = data.pct_change()
        df = df.fillna(method='bfill')
        negatives = df[df['Percentage Change'] < 0]['Percentage Change']
        sortino = (np.average(df['Percentage Change'])/np.std(negatives)) * n
        return sortino
        
    def total_return(self, data):
        '''
        Calculates total return in percentage
        '''
        return ((data[data.shape[0]-1] - data[0])/data[0]) * 100
    
    def drawDown(self, down):
        '''
        Returns maximum draw down in terms of percentage
        '''
        
        minimum = ((np.amin(down) - down[0])/down[0]) * 100
        return minimum
    
    def calmar_ratio(self, data):
        '''
        https://www.fool.com/knowledge-center/what-is-a-calmar-ratio.aspx
        '''
        drawDown = (self.drawDown(data)/100) * -1 #as multiplied by 100 in the above function
        percentage = data.pct_change()[1:]
        calmar = (np.average(percentage)/drawDown)
        return calmar