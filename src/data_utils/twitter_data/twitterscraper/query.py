from __future__ import division
import logging
import random
import requests
import datetime as dt
import json
from functools import partial
from multiprocessing.pool import Pool

from twitterscraper.tweet import Tweet

HEADERS_LIST = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0', 'Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0']


INIT_URL = "https://twitter.com/search?vertical=tweets&vertical=default&q={q}&l={lang}"
RELOAD_URL = "https://twitter.com/i/search/timeline?vertical=" \
             "default&include_available_features=1&include_entities=1&" \
             "reset_error_state=false&src=typd&max_position={pos}&q={q}&l={lang}"

def linspace(start, stop, n):
    if n == 1:
        yield stop
        return
    h = (stop - start) / (n - 1)
    for i in range(n):
        yield start + h * i


def query_single_page(url, html_response=True, retry=10, proxies=None):
    """
    Returns tweets from the given URL.

    :param url: The URL to get the tweets from
    :param html_response: False, if the HTML is embedded in a JSON
    :param retry: Number of retries if something goes wrong.
    :return: The list of tweets, the pos argument for getting the next page.
    """
    headers = {'User-Agent': random.choice(HEADERS_LIST)}

    try:
        
        if (proxies == None):
            response = requests.get(url, headers=headers)
        else:
            response = requests.get(url, proxies=proxies, headers=headers)

        if html_response:
            html = response.text or ''
        else:
            json_resp = json.loads(response.text)
            html = json_resp['items_html'] or ''
        
        tweets = list(Tweet.from_html(html))
        
        if not tweets:
            return [], None

        if not html_response:
            return tweets, json_resp['min_position']

        return tweets, "TWEET-{}-{}".format(tweets[-1].id, tweets[0].id)
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
        return query_single_page(url, html_response, retry-1, proxies=proxies)

    logging.error("Giving up.")
    return [], None


def query_tweets_once(query, proxies, limit=None, lang=''):
    """
    Queries twitter for all the tweets you want! It will load all pages it gets
    from twitter. However, twitter might out of a sudden stop serving new pages,
    in that case, use the `query_tweets` method.

    Note that this function catches the KeyboardInterrupt so it can return
    tweets on incomplete queries if the user decides to abort.

    :param query: Any advanced query you want to do! Compile it at
                  https://twitter.com/search-advanced and just copy the query!
    :param limit: Scraping will be stopped when at least ``limit`` number of
                  items are fetched.
    :param num_tweets: Number of tweets fetched outside this function.
    :return:      A list of twitterscraper.Tweet objects. You will get at least
                  ``limit`` number of items.
    """
    logging.info("Querying {}".format(query))
    query = query.replace(' ', '%20').replace("#", "%23").replace(":", "%3A")
    pos = None
    tweets = []
    
    try:
        while True:
            new_tweets, pos = query_single_page(
                INIT_URL.format(q=query, lang=lang) if pos is None
                else RELOAD_URL.format(q=query, pos=pos, lang=lang),
                pos is None, proxies=proxies
            )

            if len(new_tweets) == 0:
                logging.info("Got {} tweets for {}.".format(
                    len(tweets), query))
                return tweets

            tweets += new_tweets

            if limit and len(tweets) >= limit:
                logging.info("Got {} tweets for {}.".format(
                    len(tweets), query))
                return tweets
    except BaseException:
        logging.exception("An unknown error occurred! Returning tweets "
                          "gathered so far.")
    logging.info("Got {} tweets for {}.".format(
        len(tweets), query))
    return tweets


def eliminate_duplicates(iterable):
    """
    Yields all unique elements of an iterable sorted. Elements are considered
    non unique if the equality comparison to another element is true. (In those
    cases, the set conversion isn't sufficient as it uses identity comparison.)
    """
    class NoElement: pass

    prev_elem = NoElement
    for elem in sorted(iterable):
        if prev_elem is NoElement:
            prev_elem = elem
            yield elem
            continue

        if prev_elem != elem: 
            prev_elem = elem
            yield elem

def query_tweets(query, limit=None, begindate=dt.date(2006,3,21), enddate=dt.date.today(), poolsize=20, lang='', proxies=None, tweettype='top'):
    '''
    Params:
    _______
    
    query: (string)
    The query to search
    
    limit: (int, optional) 
    Number of tweets to scrape. Default is null
    
    tweettype: (string,optional)
    Default is top. If set to new, new tweets are scraped
    '''
    global INIT_URL, RELOAD_URL
    
    if (tweettype == 'new'):
        INIT_URL = "https://twitter.com/search?f=tweets&vertical=default&q={q}&l={lang}"
        
        RELOAD_URL = "https://twitter.com/i/search/timeline?f=tweets&vertical=" \
                     "default&include_available_features=1&include_entities=1&" \
                     "reset_error_state=false&src=typd&max_position={pos}&q={q}&l={lang}"
    
    no_days = (enddate - begindate).days
    
    if poolsize > no_days:
        # Since we are assigning each pool a range of dates to query, 
        # the number of pools should not exceed the number of dates.
        poolsize = no_days
        
    dateranges = [begindate + dt.timedelta(days=elem) for elem in linspace(0, no_days, poolsize+1)]

    if limit:
        limit_per_pool = (limit // poolsize)+1
    else:
        limit_per_pool = None

    queries = ['{} since:{} until:{}'.format(query, since, until)
               for since, until in zip(dateranges[:-1], dateranges[1:])]

    all_tweets = []
    
    if poolsize >= 1:
        try:
            pool = Pool(poolsize)

            for new_tweets in pool.imap_unordered(partial(query_tweets_once, proxies=proxies, limit=limit_per_pool, lang=lang), queries):
                all_tweets.extend(new_tweets)
                logging.info("Got {} tweets ({} new).".format(
                    len(all_tweets), len(new_tweets)))
        finally:
            pool.close()
            pool.join()

    return all_tweets
