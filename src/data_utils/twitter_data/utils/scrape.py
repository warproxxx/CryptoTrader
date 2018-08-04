import os
from glob import glob
from libs.filename_utils import get_locations

import logging
from dateutil.relativedelta import relativedelta
from twitterscraper import query_historic_tweets
import pandas as pd

from libs.reading_utils import get_proxies

class scrapeUtils:

    def __init__(self, keywords):
        self.keywords = keywords
        _, self.currRoot_dir = get_locations()
        #possibly logger

    def move_live_data(self, relative_dir="/"):
        for keyword in self.keywords:
            liveDir = self.currRoot_dir + relative_dir + "data/tweet/{}/live/*".format(keyword['coinname'])
            
            for file in glob(liveDir):
                print(file)


        # for keyword in self.keywords:
        #     moveTo = self.currRoot_dir + relative_dir + "data/tweet/{}/live_storage/*".format(keyword['coinname'])
        #     print(moveTo)

    def download_historic(self, relative_dir="/"):
        pass

    def run_twitterscraper(self):
        pass
    
    def move_twitterscraper(self):
        pass


class historicDownloader:
    def __init__(self, detailsList, logger=None, relative_dir="/"):
        '''
        Parameters:
        ___________
        
        detailsList (list): 
        List containing keyword, coinname in string and start and end in date format
        
        logger (logger):
        Saves to file if not provided else default

        relative_dir (string):
        The relative directory in which the file has to be saved
        '''
        _, self.currRoot_dir = get_locations()

        if logger == None:
            logger = logging.getLogger()
            logger.basicConfig = logging.basicConfig(filename=self.currRoot_dir + '/logs/historic_logs.txt',level=logging.INFO)
            
        self.logger = logger
        self.detailsList = detailsList
        self.relative_dir = relative_dir
        
        
    def scrape(self, start_date_time, end_date_time, form, proxy, keyword, coinname): 
        '''
        Parameters:
        ___________

        starting_date_time (datetime.datetime):
        date from which twitterscraper will scrape from twitter. Time is the additional filter user adds

        end_date_time (datetime.datetime)
        date till which twitterscraper will scrape from twitter. Time is the additional filter user adds

        form (string):
        return or save to return or save the data

        proxy (dict or None):
        dict to use a dictionary else None to not use

        keyword (string):
        Keyword to use

        coinname (string):
        To get the directory name to save
        '''                              

        start_date = start_date_time.date()
        start_timestamp = int(start_date_time.timestamp())

        end_date = end_date_time.date()
        end_timestamp = int(end_date_time.timestamp())


        delta = relativedelta(months=1) #months = 1 because multi threading takes place for each day. So upto 30 threads supported
        dic = {}
        
        while start_date <= end_date:
            temp_start=start_date

            start_date += delta

            temp_end = start_date

            if start_date > end_date:
                temp_end = end_date
            
            finalPath = self.currRoot_dir + self.relative_dir + "data/tweet/{}/historic_scrape/raw/{}_{}.csv".format(coinname.lower(), temp_start.strftime('%Y-%m-%d'), temp_end.strftime('%Y-%m-%d'))

            #do if file dosen't exisst
            if not os.path.exists(finalPath):
                df = pd.DataFrame(columns=['ID', 'Tweet', 'Time', 'User', 'Likes', 'Replies', 'Retweet', 'in_response_to', 'response_type'])

                self.logger("Current Starting Date:{} Current Ending Date:{}".format(temp_start, temp_end))
                selectedDays = (temp_end - temp_start).days
                self.logger(selectedDays)
                
                list_of_tweets = []
                list_of_tweets = query_historic_tweets(keyword, 10000 * selectedDays, begindate=temp_start, enddate=temp_end, poolsize=selectedDays, proxies=proxy)
                        
                for tweet in list_of_tweets:
                    res_type = tweet.response_type

                    if (tweet.reply_to_id == '0'):
                        res_type='tweet'
                    
                    df = df.append({'ID': tweet.id, 'Tweet': tweet.text, 'Time': tweet.timestamp, 'User': tweet.user, 'Likes': tweet.likes, 'Replies': tweet.replies, 'Retweet': tweet.retweets, 'in_response_to': tweet.reply_to_id, 'response_type': tweet.response_type}, ignore_index=True)
                    df = df[(df['Time'] >= start_timestamp) & (df['Time'] <= end_timestamp)]

                if form == "save":
                    df.to_csv(finalPath, index=False)
                else:
                    dic[temp_start.strftime("%Y-%m-%d")] = df

        if form == "return":
            return dic
                
                
    def perform_scraping(self, form = "save"):
        '''
        Parameters:
        ___________
     
        form (string):
        If set to save, the data will be saved to pandas dataframe.
        If set to return, the data will be returned as dictionary
        '''
        
        proxies = get_proxies()
        proxySize = len(proxies)
        
        all_data = {}        
        count = 0

        for coinDetail in self.detailsList:
            self.logger.info("Scraping {} Data".format(coinDetail['coinname']))
            self.logger.info("Starting Year: {} Ending Year: {}".format(coinDetail['start'].year, coinDetail['end'].year))

            proxy = proxies[count]
            
            start_date = coinDetail['start']
            end_date = coinDetail['end']
            
            delta = relativedelta(years=1)
            tData = {}
            
            while start_date <= end_date:
                temp_start=start_date

                start_date += delta

                temp_end = start_date

                if start_date > end_date:
                    temp_end = end_date
                
                if form == "save":
                    self.scrape(temp_start, temp_end, form, proxy=proxy, keyword=coinDetail['keyword'], coinname=coinDetail['coinname'])
                elif form == "return":
                    tData.update(self.scrape(temp_start, temp_end, form, proxy=proxy, keyword=coinDetail['keyword'], coinname=coinDetail['coinname']))
                    
                count +=1

                if (count >= proxySize):
                    count = 0
            
            all_data[coinDetail['coinname']] = tData
            
        if form == "return":
            return all_data