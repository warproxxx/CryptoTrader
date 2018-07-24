import os
import json
from libs.filename_utils import get_locations

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