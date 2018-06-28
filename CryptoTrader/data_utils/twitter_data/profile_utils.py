from profilescraper import query_profile
import pandas as pd
import itertools

import os

from glob import glob

import numpy as np

from proxy_utils import proxy_dict, get_proxies

from datetime import datetime, timedelta

import numba

class profileDownloader:
    def __init__(self, logger=None):
        
        if logger == None:
            logger = logging.getLogger()
            logger.basicConfig = logging.basicConfig(filename=__file__.replace('historic_utils.py', 'logs/profile_logs.txt'),level=logging.INFO)
            
        pass