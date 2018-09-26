import os
import argparse
from glob import glob
import shutil

import threading
import time
from datetime import datetime

from profilescraper import profileScraper
from twitterscraper import query_historic_tweets
from livescraper import query_live_tweets

from libs.reading_utils import get_keywords, get_proxies
from libs.writing_utils import get_logger, get_locations

from processor import historicProcessor

from collections import deque
from io import StringIO

import pandas as pd
import numpy as np

from datetime import datetime

def get_latest(files):
    if (len(files) >= 1):
        endings = [datetime.strptime(os.path.basename(file).split("_")[1].replace('.csv', ''), '%Y-%m-%d') if 'combined' not in file else datetime.strptime('2001-1-1', '%Y-%m-%d') for file in files]
        final_date = max(d for d in endings).strftime("%Y-%m-%d")
        
        for file in files:
            if final_date in file:
                with open(file, 'r') as f:
                    q = deque(f, 1)

                df = pd.read_csv(StringIO(''.join(q)), header=None)
                return df[2][0]
            
    return 0

def download_live(keywords, logger):
    qt = query_live_tweets(keywords, logger=logger)
    listener, auth = qt.get_listener(create=True)

    while True:
        try:
            qt.perform_search()
        except KeyboardInterrupt:
            logger.warning("Keyboard interrupted. Saving whatever has been collected")
            df, userData, start_time = listener.get_data()
            t1 = threading.Thread(target=qt.save_data, args=[df, userData, start_time, int(time.time())])
            t1.start()
            break
        except Exception as e:
            logger.warning(('Got an exception. Error is: {}. Saving whatever exists').format(str(e)))    
            df, userData, start_time = listener.get_data()
            t1 = threading.Thread(target=qt.save_data, args=[df, userData, start_time, int(time.time())])
            t1.start()

class runAll:
    def __init__(self, keywords, historicList, proxies, relative_dir="/"):
        '''
        Runs everything for twitter

        Parameters:
        ___________

        keywords:

        historicList:

        proxies:

        
        relative_dir:

        '''
        _, currRoot_dir = get_locations() 
        self.relative_dir = relative_dir
        self.currDir = os.path.join(currRoot_dir, relative_dir)

        self.logger = get_logger(self.currDir + '/logs/live.txt')
        self.coins = [key for key, value in keywords.items()]
        self.historicList = historicList
        
    def initial_houskeeping(self, clean):
        '''
        Cleans the folders
        '''

        if (clean == True):
            self.remove_directory_structure()

        self.create_directory_structure()
        

    def create_directory_structure(self):
        self.logger.info("Creating profile directories in case they don't exist")
        
        os.makedirs("{}/data/profile/storage/raw".format(self.currDir), exist_ok=True)
        os.makedirs("{}/data/profile/storage/interpreted".format(self.currDir), exist_ok=True)
        os.makedirs("{}/data/profile/live".format(self.currDir), exist_ok=True)
        
        for coinname in self.coins:
            os.makedirs("{}/data/tweet/{}/live".format(self.currDir, coinname), exist_ok=True)
            self.logger.info("Recreating path {}/data/tweet/{}/live if it dosen't exist".format(self.currDir, coinname))
            
            os.makedirs("{}/data/tweet/{}/historic_scrape/raw".format(self.currDir, coinname), exist_ok=True)
            self.logger.info("Recreating path {}/data/tweet/{}/historic_scrape/raw if it dosen't exist".format(self.currDir, coinname))
            os.makedirs("{}/data/tweet/{}/historic_scrape/interpreted".format(self.currDir, coinname), exist_ok=True)
            self.logger.info("Recreating path {}/data/tweet/{}/historic_scrape/interpreted if it dosen't exist".format(self.currDir, coinname))
            
            
            os.makedirs("{}/data/tweet/{}/live_storage/interpreted/top_raw".format(self.currDir, coinname), exist_ok=True)
            self.logger.info("Recreating path {}/data/tweet/{}/live_storage/interpreted/top_raw".format(self.currDir, coinname))
            os.makedirs("{}/data/tweet/{}/live_storage/interpreted/features".format(self.currDir, coinname), exist_ok=True)
            self.logger.info("Recreating path {}/data/tweet/{}/live_storage/interpreted/features".format(self.currDir, coinname))
            os.makedirs("{}/data/tweet/{}/live_storage/interpreted/network".format(self.currDir, coinname), exist_ok=True)
            self.logger.info("Recreating path {}/data/tweet/{}/live_storage/interpreted/network".format(self.currDir, coinname))
            
            os.makedirs("{}/data/tweet/{}/live_storage/archive".format(self.currDir, coinname), exist_ok=True)       
            self.logger.info("Recreating path {}/data/tweet/{}/live_storage/archive".format(self.currDir, coinname))
		
    def remove_directory_structure(self):
        for coinname in self.coins:
            self.logger.info("Removing {}/data/tweet/{}".format(self.currDir, coinname))
            shutil.rmtree("{}/data/tweet/{}".format(self.currDir, coinname))


    def get_historic_dates(self, historicScrapePath):
        '''
        Returns the latest interpreted, combined and non combined dates for historic data
        '''
        interpreted_date = 0
        combined_date = 0
        non_combined_date = 0

        try:
            final_file = os.path.join(historicScrapePath, "raw/combined.csv")

            with open(final_file, 'r') as f:
                q = deque(f, 1)

            df = pd.read_csv(StringIO(''.join(q)), header=None)
            combined_date = df[2][0]
        except Exception as e:
            pass

        try:
            final_file = os.path.join(historicScrapePath, "interpreted/data.csv")

            with open(final_file, 'r') as f:
                q = deque(f, 1)

            df = pd.read_csv(StringIO(''.join(q)), header=None)
            interpreted_date = pd.to_datetime(df[0]).astype(np.int64) // 10 ** 9
            interpreted_date = interpreted_date[0]
        except Exception as e:
            pass
        
        non_combined_date = get_latest(glob(os.path.join(os.path.join(historicScrapePath, "raw"), "*")))


        return interpreted_date, combined_date, non_combined_date

    def run_historic(self):
        historicDownloading = []
        runHistoric = 1

        for dic in self.historicList:
            historicPath = os.path.join(self.currDir, "data/tweet/{}/historic_scrape".format(dic['coinname']))
            interpreted_date, combined_date, non_combined_date = self.get_historic_dates(historicPath)
            latest_date = max(interpreted_date, combined_date, non_combined_date)
            latest_date_datetime = datetime.utcfromtimestamp(latest_date).strftime('%Y-%m-%d %H:%M:%S')
            
            if (latest_date == 0):
                historicDownloading.append(dic)

            elif (latest_date_datetime != dic['end']): #maybe timestamp in there too?
                liveRaw = os.path.join(self.currDir, "data/tweet/{}/live/raw".format(dic['coinname']))
                
                if len(glob(os.path.join(liveRaw, "*"))) >= 1:
                    runHistoric = 0
                else:
                    historicDownloading.append(dic)
            else:
                runHistoric = 0

            if (runHistoric == 1):
                qt = query_historic_tweets(historicDownloading, proxies=proxies)
                qt.perform_search()
    
    def process_historic(self, algo_name):
        hp = historicProcessor(self.historicList, algo_name, relative_dir=self.relative_dir)
        hp.read_merge(delete=True)
        hp.create_ml_features()

    def start_live(self):
        '''
        Runs live data collection in a new thread
        '''
        pass

parser = argparse.ArgumentParser()
parser.add_argument("--clean", help="Clean all log files and the temp unmoved live data", action='store_true')

options = parser.parse_args()

liveKeywords, historicList = get_keywords()

proxies = get_proxies()
    
clean = False

if options.clean:
    clean = True

ra = runAll(liveKeywords, historicList, proxies, relative_dir="test_run")
ra.initial_houskeeping(clean=clean)
# ra.run_historic()
ra.process_historic("initial_algo")
# ra.start_live()


# while True:
#     #run this in new thread
#     download_live(keywords, logger)
#     #wait for 3 hours
#     time.sleep(3 * 60 * 60)
#     #merge the live data and put it in appropriate folder

#     #Run the historic scarper. Remove tweets older than 3 hour with no existance in historic
   
#     #Fix the structure. Archive useless data.
