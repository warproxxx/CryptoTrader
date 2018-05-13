from twitterscraper import query_tweets
from datetime import datetime, date, timedelta
from dateutil.rrule import rrule, DAILY

import pandas as pd
import time

import os

def scrape(start_date, end_date, keyword="Bitcoin"):
    
    for dt in rrule(DAILY, dtstart=start_date, until=end_date):
        df = pd.DataFrame(columns=['ID', 'Tweet', 'Time', 'User', 'Likes', 'Replies', 'Retweet'])
        
        yesterday = dt - timedelta(days=1)
        tomorrow = dt + timedelta(days=1)
        
        begin = yesterday.date()
        end = tomorrow.date()
        
        print("{} {}".format(begin, end))
        list_of_tweets = query_tweets("Bitcoin", 1000, begindate=begin, enddate=end)

        for tweet in list_of_tweets:
            df = df.append({'ID': tweet.id, 'Tweet': tweet.text, 'Time': tweet.timestamp, 'User': tweet.user, 'Likes': tweet.likes, 'Replies': tweet.replies, 'Retweet': tweet.retweets}, ignore_index=True)

        df.to_csv("{}\extracted\{}.csv".format(keyword.lower(), dt.strftime('%Y-%m-%d'), index=False))
        
detailsList = []

coinDetails = {}
coinDetails['name'] = 'Bitcoin'
coinDetails['start'] = date(2013, 1, 1)
coinDetails['end'] = date(2018, 5, 12)
detailsList.append(coinDetails)

coinDetails = {}
coinDetails['name'] = 'Dashpay'
coinDetails['start'] = date(2013, 12, 15)
coinDetails['end'] = date(2018, 5, 12)
detailsList.append(coinDetails)

coinDetails = {}
coinDetails['name'] = 'Dogecoin'
coinDetails['start'] = date(2013, 1, 1)
coinDetails['end'] = date(2018, 5, 12)
detailsList.append(coinDetails)

coinDetails = {}
coinDetails['name'] = 'Ethereum'
coinDetails['start'] = date(2015, 8, 8)
coinDetails['end'] = date(2018, 5, 12)
detailsList.append(coinDetails)

coinDetails = {}
coinDetails['name'] = 'Litecoin'
coinDetails['start'] = date(2013, 5, 5)
coinDetails['end'] = date(2018, 5, 12)
detailsList.append(coinDetails)

coinDetails = {}
coinDetails['name'] = 'Monero'
coinDetails['start'] = date(2014, 5, 21)
coinDetails['end'] = date(2018, 5, 12)
detailsList.append(coinDetails)

coinDetails = {}
coinDetails['name'] = 'Ripple'
coinDetails['start'] = date(2013, 8, 5)
coinDetails['end'] = date(2018, 5, 12)
detailsList.append(coinDetails)

coinDetails = {}
coinDetails['name'] = 'Stellar'
coinDetails['start'] = date(2014, 8, 5)
coinDetails['end'] = date(2018, 5, 12)
detailsList.append(coinDetails)

for coinDetail in detailsList:
    
    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, coinDetail['name'].lower())

    if not os.path.exists(final_directory):
        os.makedirs(final_directory)
        
for coinDetail in detailsList:
    print("Scraping {} Data".format(coinDetail['name']))
    print("Starting Year: {} Ending Year: {}".format(coinDetail['start'].year, coinDetail['end'].year))
    
    for d in range(coinDetail['start'].year, coinDetail['end'].year):
        scrape(date(d,1,1), date(d, 12, 31), keyword=coinDetail['name'])