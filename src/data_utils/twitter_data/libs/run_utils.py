import os
from glob import glob
import shutil

from libs.filename_utils import get_locations

import logging

class runUtils():
    def __init__(self, keywords, logger=None):
        self.keywords = keywords
        self.coins = [key for key, value in keywords.items()]
        _, self.currRoot_dir = get_locations()  

        if (logger == None):
            self.logger = logging.getLogger()
            self.logger.basicConfig = logging.basicConfig(filename= self.currRoot_dir + '/logs/run_utils.txt', level=logging.INFO)
        else:
            self.logger = logger

    def create_directory_structure(self):
        self.logger.info("Creating profile directories in case they don't exist")
        
        os.makedirs("{}/data/profile/storage/raw".format(self.currRoot_dir), exist_ok=True)
        os.makedirs("{}/data/profile/storage/interpreted".format(self.currRoot_dir), exist_ok=True)
        os.makedirs("{}/data/profile/live".format(self.currRoot_dir), exist_ok=True)
        
        for coinname in self.coins:
            os.makedirs("{}/data/tweet/{}/live".format(self.currRoot_dir, coinname), exist_ok=True)
            self.logger.info("Recreating path {}/data/tweet/{}/live if it dosen't exist".format(self.currRoot_dir, coinname))
            
            os.makedirs("{}/data/tweet/{}/historic_scrape/raw".format(self.currRoot_dir, coinname), exist_ok=True)
            self.logger.info("Recreating path {}/data/tweet/{}/historic_scrape/raw if it dosen't exist".format(self.currRoot_dir, coinname))
            os.makedirs("{}/data/tweet/{}/historic_scrape/interpreted".format(self.currRoot_dir, coinname), exist_ok=True)
            self.logger.info("Recreating path {}/data/tweet/{}/historic_scrape/interpreted if it dosen't exist".format(self.currRoot_dir, coinname))
            
            
            os.makedirs("{}/data/tweet/{}/live_storage/interpreted/top_raw".format(self.currRoot_dir, coinname), exist_ok=True)
            self.logger.info("Recreating path {}/data/tweet/{}/live_storage/interpreted/top_raw".format(self.currRoot_dir, coinname))
            os.makedirs("{}/data/tweet/{}/live_storage/interpreted/features".format(self.currRoot_dir, coinname), exist_ok=True)
            self.logger.info("Recreating path {}/data/tweet/{}/live_storage/interpreted/features".format(self.currRoot_dir, coinname))
            os.makedirs("{}/data/tweet/{}/live_storage/interpreted/network".format(self.currRoot_dir, coinname), exist_ok=True)
            self.logger.info("Recreating path {}/data/tweet/{}/live_storage/interpreted/network".format(self.currRoot_dir, coinname))
            
            os.makedirs("{}/data/tweet/{}/live_storage/archive".format(self.currRoot_dir, coinname), exist_ok=True)       
            self.logger.info("Recreating path {}/data/tweet/{}/live_storage/archive".format(self.currRoot_dir, coinname))
            
    def remove_directory_structure(self):
        for coinname in self.coins:
            self.logger.info("Removing {}/data/tweet/{}".format(self.currRoot_dir, coinname))
            shutil.rmtree("{}/data/tweet/{}".format(self.currRoot_dir, coinname))