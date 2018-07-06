from historic_utils import historicDownloader, historicUtils
from live_utils import liveDownloader, liveUtils
from profile_utils import profileDownloader, profileUtils

from datetime import date, datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
import time

import os
from glob import glob

import threading

import pandas as pd
import numpy as np

import argparse

import logging
logging.basicConfig(filename=__file__.replace('live.py', 'logs/live.txt'),level=logging.INFO)

keywords = {'bitcoin': ['bitcoin', 'BTC'], 'dashcoin': ['dashcoin', 'DASH', 'darkcoin'], 'dogecoin': ['dogecoin', 'DOGE'], 'ethereum': ['ethereum', 'ETH'], 'litecoin': ['litecoin', 'LTC'], 'ripple': ['ripple', 'XRP'], 'monero': ['monero', 'XMR'], 'stellar': ['stellar', 'STR']}


def live_download():
    global keywords
    logging.info("Live data collector started on new thread")
    
    ld = liveDownloader(keywords)
    df, userData = ld.collect()
    
    logging.info("Live data collector thread closed")

def create_folder_structure():
    
    
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", help="Clean all log files and the temp unmoved live data", action='store_true')
    parser.print_help()
    
    options = parser.parse_args()
    
    if options.clean:
        lu = liveUtils(keywords)
        hu = historicUtils(keywords)
        
        lu.deleteFiles()
        hu.deleteFiles()
    else:
        logging.info("Starting a new thread to run the live data collector")

        t1 = threading.Thread(target=live_download)
        t1.start()

#wait for 3 hours

#merge the live data and put it in appropriate folder

#Run the historic scarper. Ther will be confusion because tweet because for tweet made 2 hour ago, bots might attempt to spread even aftger 4 hours.

#Fix the structure. Archive useless data.