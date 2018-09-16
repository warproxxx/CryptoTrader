import os
import argparse
from glob import glob
import shutil

import threading
import time

from profilescraper import profileScraper
from twitterscraper import query_historic_tweets
from livescraper import query_live_tweets

from libs.run_utils import runUtils
from libs.reading_utils import get_keywords, get_proxies
from libs.writing_utils import get_logger, get_locations

from datetime import datetime

def get_latest(files):
    if (len(files) >= 1):
        endings = [datetime.strptime(file.split("_")[1].replace('.csv', ''), '%Y-%m-%d') for file in files]
        final_date = max(d for d in endings)
        return final_date
    else:
        return None

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


parser = argparse.ArgumentParser()
parser.add_argument("--clean", help="Clean all log files and the temp unmoved live data", action='store_true')

_, currRoot_dir = get_locations()

logger = get_logger(currRoot_dir + '/logs/live.txt')

options = parser.parse_args()

keywords, historicList = get_keywords()
proxies = get_proxies()

ru = runUtils(keywords)
    
if options.clean:
    ru.remove_directory_structure()
else:
    ru.create_directory_structure()

historicDownloading = []
runHistoric = 1

for dic in historicList:
    currPath = os.path.join(currRoot_dir, "data/tweet/{}/historic_scrape/raw".format(dic['coinname']))
    final_date = get_latest(glob(os.path.join(currPath, "*")))

    if (final_date == None):
        ## Not moved to interpreted now so leaving this

        # interpretedHistoric = os.path.join(currPath, "interpreted")
        # final_date = get_latest(glob(os.path.join(interpretedHistoric, "/*")))

        # if (final_date == None):
        #     historicDownloading.append(dic)
        
        historicDownloading.append(dic)
    elif (final_date.date() != dic['end']):
        liveRaw = os.path.join(currRoot_dir, "data/tweet/{}/live/raw".format(dic['coinname']))
        
        ## Not moved or removed from interpreted so leaving this
        #liveInterpreted = os.path.join(currRoot_dir, "data/tweet/{}/live/raw".format(dic['coinname']))
        
        if len(glob(os.path.join(liveRaw, "*"))) >= 1:
            runHistoric = 0
        else:
            historicDownloading.append(dic)
    else:
        runHistoric = 0

if (runHistoric == 1):
    qt = query_historic_tweets(historicDownloading, proxies=proxies)
    qt.perform_search()

# while True:
#     #run this in new thread
#     download_live(keywords, logger)
#     #wait for 3 hours
#     time.sleep(3 * 60 * 60)
#     #merge the live data and put it in appropriate folder

#     #Run the historic scarper. Remove tweets older than 3 hour with no existance in historic
   
#     #Fix the structure. Archive useless data.
