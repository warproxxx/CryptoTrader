from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup

import pandas as pd

import time

from datetime import date
from dateutil.rrule import rrule, DAILY, MONTHLY

import os.path
import os

detailsList = []

coinDetails = {}
coinDetails['name'] = 'Bitcoin'
coinDetails['start'] = date(2013, 1, 1)
coinDetails['end'] = date(2018, 5, 12)
detailsList.append(coinDetails)

coinDetails = {}
coinDetails['name'] = 'Dashpay'
coinDetails['start'] = date(2013, 12, 15)
coinDetails['end'] = date(2018, 5, 12)
detailsList.append(coinDetails)

coinDetails = {}
coinDetails['name'] = 'Dogecoin'
coinDetails['start'] = date(2013, 1, 1)
coinDetails['end'] = date(2018, 5, 12)
detailsList.append(coinDetails)

coinDetails = {}
coinDetails['name'] = 'Ethereum'
coinDetails['start'] = date(2015, 8, 8)
coinDetails['end'] = date(2018, 5, 12)
detailsList.append(coinDetails)

coinDetails = {}
coinDetails['name'] = 'Litecoin'
coinDetails['start'] = date(2013, 5, 5)
coinDetails['end'] = date(2018, 5, 12)
detailsList.append(coinDetails)

coinDetails = {}
coinDetails['name'] = 'Monero'
coinDetails['start'] = date(2014, 5, 21)
coinDetails['end'] = date(2018, 5, 12)
detailsList.append(coinDetails)

coinDetails = {}
coinDetails['name'] = 'Ripple'
coinDetails['start'] = date(2013, 8, 5)
coinDetails['end'] = date(2018, 5, 12)
detailsList.append(coinDetails)

coinDetails = {}
coinDetails['name'] = 'Stellar'
coinDetails['start'] = date(2014, 8, 5)
coinDetails['end'] = date(2018, 5, 12)
detailsList.append(coinDetails)