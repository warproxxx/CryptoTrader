from twitterscraper import query_tweets
from datetime import datetime, date, timedelta
from dateutil.rrule import rrule, DAILY

import pandas as pd
import time


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

for d in range(2013, 2018):
    scrape(date(d,1,1), date(d, 12, 31))