import os
import json
from libs.writing_utils import get_locations
from datetime import date, datetime
import numpy as np
import re
import pandas as pd

def proxy_dict(address):
    '''
    Parameters:
    ___________
    address: (string)
    IP Address

    Returns:
    ________
    proxyDict: (dict)
    Converts the IP into dictionary containing the value as http, https and ftp
    '''

    http_proxy  = "http://{}".format(address)
    https_proxy = "https://{}".format(address)
    ftp_proxy   = "ftp://{}".format(address)

    proxyDict = { 
                  "http"  : http_proxy, 
                  "https" : https_proxy, 
                  "ftp"   : ftp_proxy
                }
    
    return proxyDict

def get_proxies(proxyFile="/data/static/proxies.txt"):
    '''
    Parameters:
    ___________
    proxyFile (string):
    Location of the file relative to twitter_data folder

    Returns:
    ________
    proxies (dict):
    Returns list of all proxies in usable format containing value as http, https and ftp as dictionary
    '''

    _, rootDir = get_locations()
    toOpen = rootDir + proxyFile

    a = open(toOpen)

    proxies = []

    for line in a.readlines():
        proxy = proxy_dict(line.replace('\n', ''))
        proxies.append(proxy)
        
    return proxies

def get_custom_keywords(liveKeywords, starting, ending):
    '''
    Build keyword of custom type

    Parameters:
    ___________
    liveKeywords (dict):
    Dictionary of coin name and it's keywords

    starting (date or datetime):
    starting point

    ending (date or datetime):
    ending point
    '''
    historicList = []

    for coinname, keyword in liveKeywords.items():
        historicList.append({'keyword': ' OR '.join(keyword), 'coinname': coinname, 'start': starting, 'end': ending})

    return historicList


def get_keywords(keywordsFile="/keywords.json", ending=datetime.now()):
    '''
    Parameters:
    ___________
    keywordsFile (string):
    Location of the file containing keywords relative to twitter_data folder

    ending (date):
    The ending date for historic data. today's date by default

    Returns:
    ________
    liveKeywords, historicList: 
    liveKeywords is keywords for live data. HistoricList is what i have called detailsList. Used for historic data
    '''
    
    _, rootDir = get_locations()
    toOpen = rootDir + keywordsFile

    with open(toOpen) as json_file:
        json_data = json.load(json_file)

    liveKeywords = {}
    historicList = []

    for coinname in json_data:
        liveKeywords[coinname] = json_data[coinname]["keywords"]
        historicList.append({'keyword': ' OR '.join(json_data[coinname]["keywords"]), 'coinname': coinname, 'start': datetime.strptime(json_data[coinname]["start_date"], "%Y-%m-%d"), 'end': ending})
    
    return liveKeywords, historicList


def get_twitter(twitterFile="/data/static/api.json"):
    '''
    Parameters:
    ___________
    twitterFile (string):
    Location of the file containing twitter API credentials relative to twitter_data folder

    Returns:
    ________
    consumber_key, consumers_secret, access_token, access_token_secret
    '''

    _, rootDir = get_locations()
    toOpen = rootDir + twitterFile

    with open(toOpen) as json_file:
        json_data = json.load(json_file) 
    
    return json_data['consumer_key'], json_data['consumer_secret'], json_data['access_token'], json_data['access_token_secret']

def cleanData(data):
    pattern = [ 'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',  # URLs'
                '([^a-zA-Z0-9,.!? ]+?)', #anything else except text and punctuations
                ]

    sub_pattern = re.compile('|'.join(pattern))
    
    if isinstance(data, pd.Series):
        data = data.str.lower()
        replaced = data.str.replace(sub_pattern, '').str.strip()
    else:

        data = data.lower()
        replaced = re.sub(sub_pattern, '', word).strip()
        
    return replaced