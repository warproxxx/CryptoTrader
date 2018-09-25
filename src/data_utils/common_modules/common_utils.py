from io import BytesIO
from ta import *
import os

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

    Returns:
    ________
    initial_date(string):
    The first date in files

    final_date(string):
    The final date in files

    combined (BytesIO):
    BytesIO of the files
    '''
    combined = BytesIO()
    first = 1
    all_dates = []
    for file in files:
        if (ignore_name != None):
            if ignore_name in file:
                continue
        
        all_dates.extend(os.path.splitext(os.path.basename(file))[0].split("_"))

        with open(file, "rb") as f:
            if (first != 1):
                next(f)                
            else:
                first = 0
            
            combined.write(f.read())

    combined.seek(0)
    #df = pd.read_csv(combined, lineterminator='\n')
    all_dates = sorted(all_dates, key=lambda d: tuple(map(int, d.split('-'))))
    
    return all_dates[0], all_dates[-1], combined