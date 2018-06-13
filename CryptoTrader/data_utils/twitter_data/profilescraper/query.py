from multiprocessing.pool import Pool
import requests
import json
import random
import logging
import time

from functools import partial

from profilescraper.profile import Profile

HEADERS_LIST = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0', 'Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0']

def query_single_profile(url, retry=10, proxies=None):
    logging.info("Querying {}".format(url))
    
    headers = {'User-Agent': random.choice(HEADERS_LIST)}

    try:
        if (proxies == None):
            response = requests.get(url, headers=headers)
        else:
            response = requests.get(url, headers=headers, proxies=proxies)

        html = response.text or ''

        profiles = list(Profile.from_html(html))

        if not profiles:
            return []

        return profiles
    except requests.exceptions.HTTPError as e:
        logging.exception('HTTPError {} while requesting "{}"'.format(
            e, url))
    except requests.exceptions.ConnectionError as e:
        logging.exception('ConnectionError {} while requesting "{}"'.format(
            e, url))
    except requests.exceptions.Timeout as e:
        logging.exception('TimeOut {} while requesting "{}"'.format(
            e, url))
    except json.decoder.JSONDecodeError as e:
        logging.exception('Failed to parse JSON "{}" while requesting "{}".'.format(
            e, url))
    except ValueError as e:
        logging.exception('Failed to parse JSON "{}" while requesting "{}"'.format(e, url))

    if retry > 0:
        logging.info("Retrying... (Attempts left: {})".format(retry))
        return query_single_profile(url, retry-1, proxies=proxies)
    
    logging.error("Giving up.")
    return []


def query_profile(profiles, poolsize=20, proxies=None):
    '''
    profiles: List
    Unique profies to scrape from

    poolsize: int
    Size of pool. Bigger - the more instance of browser is opened
    '''
    url = "https://twitter.com/{}"
    no_profiles = len(profiles)

    if (poolsize > no_profiles):
        poolsize = no_profiles

    urls = [url.format(x) for x in profiles]
    all_profile = []

    pool = Pool(poolsize)

    try:
        for profile_data in pool.imap_unordered(partial(query_single_profile, proxies=proxies), urls):
            all_profile.extend(profile_data)
            logging.info("Got {} profiles ({} new).".format(
                len(all_profile), len(profile_data)))

    finally:
        pool.close()
        pool.join()

    return all_profile
    
