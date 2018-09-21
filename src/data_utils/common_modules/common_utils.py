from io import BytesIO
from ta import *

def trends_ta(df, column):
    '''
    Performs Technical Analysis on the given column
    '''
    
    df['{}_ema_12'.format(column)] = ema_indicator(df[column], n=12)
    df['{}_ema_26'.format(column)] = ema_indicator(df[column], n=26)

    df['{}_macd'.format(column)] = macd(df[column])

    df['{}_rsi'.format(column)] = rsi(df[column])
    df['{}_rsi_movement'.format(column)] = df['{}_rsi'.format(column)].pct_change().fillna(method='bfill')

    df['{}_ma_12'.format(column)] = df[column].rolling(12).sum().fillna(method='bfill')
    df['{}_ma_26'.format(column)] = df[column].rolling(26).sum().fillna(method='bfill')
    df['{}_ma_12_movement'.format(column)] = df['{}_ma_12'.format(column)].pct_change().fillna(method='bfill')
    df['{}_ma_26_movement'.format(column)] = df['{}_ma_26'.format(column)].pct_change().fillna(method='bfill')

    df['{}_movement'.format(column)] = df[column].pct_change().fillna(method='bfill')

    df['{}_trix'.format(column)] = trix(df[column])

    df['{}_momentum_3'.format(column)]  = df[column]/df.shift(3)[column] #divide by the interest 3 days ago
    df['{}_momentum_3'.format(column)] = df['{}_momentum_3'.format(column)].fillna(method='bfill')
    df['{}_momentum_6'.format(column)]  = df[column]/df.shift(6)[column]
    df['{}_momentum_6'.format(column)] = df['{}_momentum_6'.format(column)].fillna(method='bfill')
    df['{}_momentum_9'.format(column)]  = df[column]/df.shift(9)[column]
    df['{}_momentum_9'.format(column)] = df['{}_momentum_9'.format(column)].fillna(method='bfill')


    df['{}_disparity_12'.format(column)] = df[column] / df['{}_ma_12'.format(column)]
    df['{}_disparity_26'.format(column)] = df[column] / df['{}_ma_26'.format(column)]
    df['{}_disparity_12_movement'.format(column)] = df['{}_disparity_12'.format(column)].pct_change().fillna(method='bfill')
    df['{}_disparity_26_movement'.format(column)] = df['{}_disparity_26'.format(column)].pct_change().fillna(method='bfill')

    return df

def merge_csvs(files, ignore_name=None):
    '''
    Appends csvs and returns

    Parameters:
    ___________

    files (List):
    List of files to append
    '''
    combined = BytesIO()
    first = 1

    for file in files:
        if (ignore_name != None):
            if "combined.csv" in file:
                continue
                
        with open(file, "rb") as f:
            if (first != 1):
                next(f)                
            else:
                first = 0
            
            combined.write(f.read())

    combined.seek(0)
    #df = pd.read_csv(combined, lineterminator='\n')

    return combined