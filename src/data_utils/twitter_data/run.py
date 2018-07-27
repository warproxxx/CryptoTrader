from profilescraper import query_profile
from twitterscraper import query_historic_tweets
from livescraper import query_live_tweets

from libs.run_utils import runUtils
from libs.reading_utils import get_keywords

import argparse

import logging
logging.basicConfig(filename=__file__.replace('live.py', 'logs/live.txt'),level=logging.INFO)

    
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", help="Clean all log files and the temp unmoved live data", action='store_true')
    parser.print_help()
    
    options = parser.parse_args()
    keywords, historicList = get_keywords()
    ru = runUtils(keywords)
    
    if options.clean:
        ru.remove_directory_structure()
    else:
        ru.create_directory_structure()

#start the live data collector
#download first time historical data

#wait for 3 hours

#merge the live data and put it in appropriate folder

#Run the historic scarper. Ther will be confusion because tweet because for tweet made 2 hour ago, bots might attempt to spread even aftger 4 hours.

#Fix the structure. Archive useless data.