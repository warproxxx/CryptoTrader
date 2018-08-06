import os
from glob import glob
from libs.writing_utils import get_locations

import logging
from dateutil.relativedelta import relativedelta
from twitterscraper import twitterScraper
import pandas as pd

from libs.reading_utils import get_proxies
from libs.writing_utils import get_logger, get_locations

class scrapeUtils:

    def __init__(self, keywords, logger=None):
        self.keywords = keywords
        _, self.currRoot_dir = get_locations()
        
        if (logger == None):
            self.logger = get_logger(self.currRoot_dir + "/logs/scrape.log")
        else:
            self.logger = logger

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