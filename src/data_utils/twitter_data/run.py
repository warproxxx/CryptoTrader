from profilescraper import query_profile
from twitterscraper import query_historic_tweets
from livescraper import query_live_tweets

from libs.run_utils import runUtils
from libs.reading_utils import get_keywords
from libs.filename_utils import get_locations

import argparse

import time
import threading

import logging

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


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", help="Clean all log files and the temp unmoved live data", action='store_true')
    parser.print_help()
    
    _, currRoot_dir = get_locations()

    logger = logging.getLogger()
    logger.basicConfig = logging.basicConfig(filename= currRoot_dir + '/logs/live.txt', level=logging.INFO)

    options = parser.parse_args()
    keywords, historicList = get_keywords()
    ru = runUtils(keywords, logger=logger)

     
    if options.clean:
        ru.remove_directory_structure()
    else:
        ru.create_directory_structure()

    download_live(keywords, logger)

#start the live data collector

#download first time historical data

#wait for 3 hours

#merge the live data and put it in appropriate folder

#Run the historic scarper. Ther will be confusion because tweet because for tweet made 2 hour ago, bots might attempt to spread even aftger 4 hours.

#Fix the structure. Archive useless data.
