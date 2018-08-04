from twitterscraper import query_historic_tweets

from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY
from datetime import datetime, date, timedelta

from libs.reading_utils import get_proxies
from libs.filename_utils import get_locations

import pandas as pd
import time

import os

import numpy as np

import requests

from glob import glob

import logging


                    
