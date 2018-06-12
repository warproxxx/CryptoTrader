from multiprocessing.pool import Pool
import requests
import json
import random
import logging

HEADERS_LIST = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0', 'Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0']

def query_single_profile(url, retries=10, proxies=None):
    headers = {'User-Agent': random.choice(HEADERS_LIST)}

    if (proxies == None):
        response = requests.get(url, headers=headers)
    else:
        response = requests.get(url, headers=headers, proxies=proxies)

    html = response.text or ''


def query_profile(profiles, poolsize=20, proxies=None):
    '''
    profiles: List
    Unique profies to scrape from

    poolsize: int
    Size of pool. Bigger - the more instance of browser is opened
    '''
    url = "https://twitter.com/{}"
    

    
