import os
import pandas as pd
from libs.writing_utils import get_locations, get_logger
from glob import glob

import sys
sys.path.append(os.path.dirname(get_locations()[1]))

from common_modules.common_utils import merge_csvs

class historicProcessor:
    '''
    Processor for historic data
    '''

    def __init__(self, detailsList, relative_dir="/", logger=None):
        '''
        Parameters:
        ___________
        detailsList (list): 
        List containing keyword, coinname in string and start and end in date format

        relative_dir (string):
        The relative directory 
        '''
        _, self.currRoot_dir = get_locations()

        if logger == None:
            self.logger = get_logger(self.currRoot_dir + "/logs/twitterscraper.log")
        else:
            self.logger = logger

        self.detailsList = detailsList
        self.relative_dir = relative_dir

    def read_merge(self, delete=True):
        '''
        Reads many csv files and combines them to one

        Paramters:
        _________
        delete (boolean): Deletes the read file later if set to true
        '''

        for coinDetail in self.detailsList:
            path = os.path.join(self.currRoot_dir, self.relative_dir, "data/tweet/{}/historic_scrape/raw".format(coinDetail['coinname']))

            files = glob(path + "/*")
            f = merge_csvs(files, ignore_name="combined.csv")

            if (delete==True):
                for file in files:
                    os.remove(file)

            with open(os.path.join(path, "combined.csv"), "wb") as out:
                out.write(f.read())

    def create_ml_features(self):
        '''
        Create features from these textual data
        '''

        for coinDetail in self.detailsList:
            path = os.path.join(self.currRoot_dir, self.relative_dir, "data/tweet/{}/historic_scrape/raw".format(coinDetail['coinname']))

        #Doc2Vec is useless. I just need the top sentiment, and the bot sentiments. And find out what they trying
    def create_visualization_features(self):
        pass