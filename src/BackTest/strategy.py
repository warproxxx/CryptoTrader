import numpy as np
import pandas as pd
from data_utils import BasicFunctions, PriceFunctions

from BackTest import Backtester

from keras.layers import Input, Dense, LSTM, Conv1D, MaxPooling1D, Activation, Dropout, BatchNormalization
from keras.models import Model

class strategyBacktest():
    
    def __init__(self, bar, features='', conditions='', trainSize=0.8):
        '''
        Parameters:
        ___________
        
        bar: 
        Pandas Dataframe containing Date, Open, High, Low, Close and Volume
        
        features: 
        The Features to use to predict during this prediction. Data and other column of pandas features
        
        conditions: 
        Conditions to apply using the features
        
        '''
        self.bar = bar
        self.features = features
        self.conditions = conditions
        self.trainSize = trainSize
        
        self.y = pd.DataFrame(columns={'Percentage Change', 'Classification'})
        self.y['Percentage Change'] = (1 - self.bar['Close']/self.bar.shift(-1)['Close'])
        self.y['Classification'] = self.y['Percentage Change'] > 0
        self.y['Classification'] = self.y['Classification'] * 1
        
        self.y = self.y.fillna(method='ffill')
        
    def get_Model(self):
        inp = Input(shape=(None, self.features.shape[1]))
        
        x = LSTM(32)(inp)
        x = BatchNormalization()(x)
        x = Dropout(0.4)(x)
        
        x = Dense(5, activation='elu')(x)
        x = BatchNormalization()(x)
        x = Dropout(0.4)(x)
        
        x = Dense(2, activation='elu')(x)
        x = BatchNormalization()(x)
        x = Dropout(0.4)(x)
        
        model = Model(inp, x)
        
        #print(model.summary())
        
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model
        
    def mlBacktest(self):
        
        if ('Date' in self.features):
            dates = self.features['Date']
            self.features = self.features.drop('Date', axis=1)
            
        X = np.asarray(self.features)
        Y = np.asarray(self.y)
        
        print('Real Y')
        bars = {}
        signals = {}
        
        bars['BTC'] = self.bar
        signals['BTC'] = Y
        
        bt = Backtester(bars, signals, comission=0)
        bt.perform_backtest()
        bt.get_outcome()
                
        
        
        model = self.get_Model()
        model.fit(x=X.reshape(-1, 1, self.features.shape[1]), y=Y, batch_size=16, epochs=1000)
        
        ypred = model.predict(X.reshape(-1, 1, self.features.shape[1]))
        
        print('Features based Y prediction')
        
        signals = {}
        signals['BTC'] = ypred
        
        print(signals['BTC'].shape)
        
        bars = {}
        bars['BTC'] = self.bar
        
        print(bars['BTC'].shape)
        
        
        bt1 = Backtester(bars, signals, comission=0)
        bt1.perform_backtest()
        pos = bt1.get_positions()
        print(pos)
        bt1.get_outcome()