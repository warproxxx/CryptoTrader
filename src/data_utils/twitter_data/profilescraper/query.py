from multiprocessing.pool import Pool
import requests
import json
import random
import time

import logging

from functools import partial

from libs.writing_utils import get_logger, get_locations

from profilescraper.profile import Profile

HEADERS_LIST = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0', 'Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0']

def query_single_profile(url, logger, retry=10, proxy=None):
    logger.info("Querying {}".format(url))
    
    headers = {'User-Agent': random.choice(HEADERS_LIST)}

    try:
        if (proxy == None):
            response = requests.get(url, headers=headers)
        else:
            response = requests.get(url, headers=headers, proxies=proxy)

        html = response.text or ''

        profile = Profile.from_html(html)

        if not profile:
            return 0

        return profile
    except requests.exceptions.HTTPError as e:
        logger.exception('HTTPError {} while requesting "{}"'.format(
            e, url))
    except requests.exceptions.ConnectionError as e:
        logger.exception('ConnectionError {} while requesting "{}"'.format(
            e, url))
    except requests.exceptions.Timeout as e:
        logger.exception('TimeOut {} while requesting "{}"'.format(
            e, url))
    except json.decoder.JSONDecodeError as e:
        logger.exception('Failed to parse JSON "{}" while requesting "{}".'.format(
            e, url))
    except ValueError as e:
        logger.exception('Failed to parse JSON "{}" while requesting "{}"'.format(e, url))

    if retry > 0:
        logger.info("Retrying... (Attempts left: {})".format(retry))
        return query_single_profile(url, retry-1, proxy=proxy)
    
    logger.error("Giving up.")
    return 0


def query_profile(profiles, logger, poolsize=20, proxy=None):
    '''
    profiles: List
    Unique profies to scrape from

    poolsize: int
    Size of pool. Bigger - the more instance of browser is opened

    logger (logger):
    Made this mandatory here because of issues
    '''
    _, rootDir = get_locations()
    
    url = "https://twitter.com/{}"
    no_profiles = len(profiles)

    if (poolsize > no_profiles):
        poolsize = no_profiles

    urls = [url.format(x) for x in profiles]
    all_profile = []

    pool = Pool(poolsize)

    try:
        for profile_data in pool.imap_unordered(partial(query_single_profile, proxy=proxy, logger=logger), urls):
            all_profile.append(profile_data)
            logger.info("Got {} profiles (1 new).".format(len(all_profile)))

    finally:
        pool.close()
        pool.join()

    return all_profile
    
