from historic_utils import historicDownloader, historicUtils
from live_utils import liveDownloader, liveUtils
from profile_utils import profileDownloader, profileUtils

from datetime import date, datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
import time

import os
from glob import glob
import shutil

import threading

import pandas as pd
import numpy as np

import argparse

import logging
logging.basicConfig(filename=__file__.replace('live.py', 'logs/live.txt'),level=logging.INFO)

class liveManager():
    def __init__(self, keywords= {'bitcoin': ['bitcoin', 'BTC'], 'dashcoin': ['dashcoin', 'DASH', 'darkcoin'], 'dogecoin': ['dogecoin', 'DOGE'], 'ethereum': ['ethereum', 'ETH'], 'litecoin': ['litecoin', 'LTC'], 'ripple': ['ripple', 'XRP'], 'monero': ['monero', 'XMR'], 'stellar': ['stellar', 'STR']}):
        self.keywords = keywords
        self.coins = [key for key, value in keywords.items()]
        self.currdir = os.path.realpath(__file__).replace("/live.py", "")    
    
    def live_download(self):
        logging.info("Live data collector started on new thread")

        ld = liveDownloader(self.keywords)
        df, userData = ld.collect()

        logging.info("Live data collector thread closed")

    def create_directory_structure(self):
        logging.info("Creating profile directories in case they don't exist".format(self.currdir, coinname))
        
        os.makedirs("{}/data/profile/storage/raw".format(self.currdir), exist_ok=True)
        os.makedirs("{}/data/profile/storage/interpreted".format(self.currdir), exist_ok=True)
        os.makedirs("{}/data/profile/live".format(self.currdir), exist_ok=True)
        
        for coinname in self.coins:
            os.makedirs("{}/data/tweet/{}/live".format(self.currdir, coinname), exist_ok=True)
            logging.info("Recreating path {}/data/tweet/{}/live if it dosen't exist".format(self.currdir, coinname))
            
            os.makedirs("{}/data/tweet/{}/historic_scrape/raw".format(self.currdir, coinname), exist_ok=True)
            logging.info("Recreating path {}/data/tweet/{}/historic_scrape/raw if it dosen't exist".format(self.currdir, coinname))
            os.makedirs("{}/data/tweet/{}/historic_scrape/interpreted".format(self.currdir, coinname), exist_ok=True)
            logging.info("Recreating path {}/data/tweet/{}/historic_scrape/interpreted if it dosen't exist".format(self.currdir, coinname))
            
            
            os.makedirs("{}/data/tweet/{}/live_storage/interpreted/top_raw".format(self.currdir, coinname), exist_ok=True)
            logging.info("Recreating path {}/data/tweet/{}/live_storage/interpreted/top_raw".format(self.currdir, coinname))
            os.makedirs("{}/data/tweet/{}/live_storage/interpreted/features".format(self.currdir, coinname), exist_ok=True)
            logging.info("Recreating path {}/data/tweet/{}/live_storage/interpreted/features".format(self.currdir, coinname))
            os.makedirs("{}/data/tweet/{}/live_storage/interpreted/network".format(self.currdir, coinname), exist_ok=True)
            logging.info("Recreating path {}/data/tweet/{}/live_storage/interpreted/network".format(self.currdir, coinname))
            
            os.makedirs("{}/data/tweet/{}/live_storage/archive".format(self.currdir, coinname), exist_ok=True)       
            logging.info("Recreating path {}/data/tweet/{}/live_storage/archive".format(self.currdir, coinname))
            
    def remove_directory_structure(self):
        for coinname in self.coins:
            logging.info("Removing {}/data/tweet/{}".format(self.currdir, coinname))
            shutil.rmtree("{}/data/tweet/{}".format(self.currdir, coinname))
            
    
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", help="Clean all log files and the temp unmoved live data", action='store_true')
    parser.print_help()
    
    options = parser.parse_args()
    lm = liveManager()
    
    if options.clean:
        lu = liveUtils(keywords)
        hu = historicUtils(keywords)
        
        lu.deleteFiles()
        hu.deleteFiles()
    else:
        lm.remove_directory_structure()
#         logging.info("Starting a new thread to run the live data collector")

#         t1 = threading.Thread(target=lm.live_download)
#         t1.start()

#wait for 3 hours

#merge the live data and put it in appropriate folder

#Run the historic scarper. Ther will be confusion because tweet because for tweet made 2 hour ago, bots might attempt to spread even aftger 4 hours.

#Fix the structure. Archive useless data.