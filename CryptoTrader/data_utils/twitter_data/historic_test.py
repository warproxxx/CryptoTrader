from historic_utils import historicDownloader, historicUtils
from datetime import date, datetime
import logging


keywords = {'bitcoin': ['bitcoin', 'BTC'], 'dashcoin': ['dashcoin', 'DASH', 'darkcoin'], 'dogecoin': ['dogecoin', 'DOGE'], 'ethereum': ['ethereum', 'ETH'], 'litecoin': ['litecoin', 'LTC'], 'ripple': ['ripple', 'XRP'], 'monero': ['monero', 'XMR'], 'stellar': ['stellar', 'STR']}

keywordsAll = [value for key, values in keywords.items()
                       for value in values]

today = date(datetime.now().year, datetime.now().month, datetime.now().day)

detailsList = []

for key, values in keywords.items():
    
    start = {
        'bitcoin': date(2015, 1, 1),
        'dashcoin': date(2015, 5, 1),
        'dogecoin': date(2015, 1, 1),
        'ethereum': date(2015, 12, 1),
        'litecoin': date(2015, 1, 1),
        'monero': date(2015, 1, 1),
        'ripple': date(2015, 1, 1),
        'stellar': date(2015, 1, 1)
    }[key]
    
    detailsList.append({'keyword': ' OR '.join(values), 'coinname': key, 'start': start, 'end': today})
    
hd = historicDownloader(detailsList)
hu = historicUtils(detailsList)

hd.perform_scraping()