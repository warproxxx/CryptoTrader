from __future__ import division
import random
import requests
import datetime as dt
import json
from functools import partial
from multiprocessing.pool import Pool

import os
import pandas as pd

from dateutil.relativedelta import relativedelta

from twitterscraper.tweet import Tweet

from libs.writing_utils import get_locations, get_logger
from libs.reading_utils import get_proxies

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

def linspace(start, stop, n):
    if n == 1:
        yield stop
        return
    h = (stop - start) / (n - 1)
    for i in range(n):
        yield start + h * i

class twitterScraper:
    def __init__(self, proxy=None, logger=None):
        '''
        Parameters:
        ___________
        logger: (logger)
        logger object to log all this

        proxy: (dict)
        Single Proxy to use or None. Dictionary containing http, https and ftp proxy to use for using with requests
        '''

        self.HEADERS_LIST = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0', 'Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0']


        self.INIT_URL = "https://twitter.com/search?vertical=tweets&vertical=default&q={q}&l={lang}"
        self.RELOAD_URL = "https://twitter.com/i/search/timeline?vertical=" \
                    "default&include_available_features=1&include_entities=1&" \
                    "reset_error_state=false&src=typd&max_position={pos}&q={q}&l={lang}"
        _, self.currRoot = get_locations()

        if logger == None:
            self.logger = get_logger(self.currRoot + "/logs/twitterscraper.log")
        else:
            self.logger = logger

        self.proxy = proxy


    def query_single_page(self, url, html_response=True, retry=10):
        """
        Returns tweets from the given URL.

        :param url: The URL to get the tweets from
        :param html_response: False, if the HTML is embedded in a JSON
        :param retry: Number of retries if something goes wrong.
        :return: The list of tweets, the pos argument for getting the next page.
        """
        headers = {'User-Agent': random.choice(self.HEADERS_LIST)}

        try:
            
            if (self.proxy == None):
                response = requests.get(url, headers=headers)
            else:
                response = requests.get(url, proxies=self.proxy, headers=headers)

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
            self.logger.exception('HTTPError {} while requesting "{}"'.format(
                e, url))
        except requests.exceptions.ConnectionError as e:
            self.logger.exception('ConnectionError {} while requesting "{}"'.format(
                e, url))
        except requests.exceptions.Timeout as e:
            self.logger.exception('TimeOut {} while requesting "{}"'.format(
                e, url))
        except json.decoder.JSONDecodeError as e:
            self.logger.exception('Failed to parse JSON "{}" while requesting "{}".'.format(
                e, url))
        except ValueError as e:
            self.logger.exception('Failed to parse JSON "{}" while requesting "{}"'.format(e, url))
            
        if retry > 0:
            self.logger.info("Retrying... (Attempts left: {})".format(retry))
            return self.query_single_page(url, html_response, retry-1)

        self.logger.error("Giving up.")
        return [], None


    def query_tweets_once(self, query, limit=None, lang=''):
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
        self.logger.info("Querying {}".format(query))
        query = query.replace(' ', '%20').replace("#", "%23").replace(":", "%3A")
        pos = None
        tweets = []
        
        try:
            while True:
                new_tweets, pos = self.query_single_page(
                    self.INIT_URL.format(q=query, lang=lang) if pos is None
                    else self.RELOAD_URL.format(q=query, pos=pos, lang=lang),
                    pos is None
                )

                if len(new_tweets) == 0:
                    self.logger.info("Got {} tweets for {}.".format(
                        len(tweets), query))
                    return tweets

                tweets += new_tweets

                if limit and len(tweets) >= limit:
                    self.logger.info("Got {} tweets for {}.".format(
                        len(tweets), query))
                    return tweets
        except BaseException:
            self.logger.exception("An unknown error occurred! Returning tweets "
                            "gathered so far.")
        self.logger.info("Got {} tweets for {}.".format(
            len(tweets), query))
        return tweets

    def query_tweets(self, query, limit=None, begindate=dt.date(2006,3,21), enddate=dt.date.today(), poolsize=20, lang='', tweettype='top'):
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

                for new_tweets in pool.imap_unordered(partial(self.query_tweets_once, limit=limit_per_pool, lang=lang), queries):
                    all_tweets.extend(new_tweets)
                    self.logger.info("Got {} tweets ({} new).".format(
                        len(all_tweets), len(new_tweets)))
            finally:
                pool.close()
                pool.join()

        return all_tweets


class query_historic_tweets():
    def __init__(self, detailsList, proxies=None, logger=None, relative_dir="/"):
        '''
        Parameters:
        ___________
        detailsList (list): 
        List containing keyword, coinname in string and start and end in date format
        
        proxies (list of dict or None):
        list of dict in proxies format (containing http, https and ftp) to use for each next query. Else None to not use

        logger (logger):
        Saves to file if not provided else default
        '''

        _, self.currRoot_dir = get_locations()

        if logger == None:
            self.logger = get_logger(self.currRoot_dir + "/logs/twitterscraper.log")
        else:
            self.logger = logger

        self.detailsList = detailsList
        self.relative_dir = relative_dir
        self.proxies = proxies

    def scrape(self, start_date_time, end_date_time, proxy, form, keyword, coinname): 
        '''
        To scrape data from custom timeframe in twitter

        Parameters:
        ___________

        starting_date_time (datetime.datetime):
        date from which twitterscraper will scrape from twitter. Time is the additional filter user adds

        end_date_time (datetime.datetime)
        date till which twitterscraper will scrape from twitter. Time is the additional filter user adds

        proxy (dict or None):
        Single proxy dictionary to use containing http, https and ftp

        form (string):
        return or save to return or save the data

        keyword (string):
        Keyword to use

        coinname (string):
        To get the directory name to save
        '''                              

        start_date = start_date_time.date()
        start_timestamp = int(start_date_time.timestamp())

        end_date = end_date_time.date()
        end_timestamp = int(end_date_time.timestamp())


        delta = relativedelta(months=1) #months = 1 because multi threading takes place for each day. So upto 30 threads supported
        dic = {}
        
        while start_date <= end_date:
            temp_start=start_date

            start_date += delta

            temp_end = start_date

            if start_date > end_date:
                temp_end = end_date
            
            finalPath = self.currRoot_dir + self.relative_dir + "data/tweet/{}/historic_scrape/raw/{}_{}.csv".format(coinname.lower(), temp_start.strftime('%Y-%m-%d'), temp_end.strftime('%Y-%m-%d'))

            #do if file dosen't exisst
            if not os.path.exists(finalPath):
                df = pd.DataFrame(columns=['ID', 'Tweet', 'Time', 'User', 'Likes', 'Replies', 'Retweets', 'in_response_to', 'response_type'])

                self.logger.info("Current Starting Date:{} Current Ending Date:{}".format(temp_start, temp_end))
                selectedDays = (temp_end - temp_start).days
                self.logger.info(selectedDays)
                
                list_of_tweets = []
                list_of_tweets = twitterScraper(proxy=proxy, logger=self.logger).query_tweets(keyword, 10000 * selectedDays, begindate=temp_start, enddate=temp_end, poolsize=selectedDays)
                
                for tweet in list_of_tweets:
                    res_type = tweet.response_type

                    if (tweet.reply_to_id == '0'):
                        res_type='tweet'
                    
                    df = df.append({'ID': tweet.id, 'Tweet': tweet.text, 'Time': tweet.timestamp, 'User': tweet.user, 'Likes': tweet.likes, 'Replies': tweet.replies, 'Retweets': tweet.retweets, 'in_response_to': tweet.reply_to_id, 'response_type': tweet.response_type}, ignore_index=True)

                    
                df = df[pd.to_numeric(df['Time'], errors='coerce').notnull()]
                df['Time'] = df['Time'].astype(int)

                df = df[(df['Time'] >= start_timestamp) & (df['Time'] <= end_timestamp)]

                if form == "save":
                    df.to_csv(finalPath, index=False)
                else:
                    dic[temp_start.strftime("%Y-%m-%d")] = df

        if form == "return":
            return dic

    def perform_search(self, form = "save"):
        '''
        To scrape data from custom timeframe in twitter for long dates. Scrapes a month at a time

        Parameters:
        ___________
        To do one month at a time
     
        form (string):
        If set to save, the data will be saved to pandas dataframe.
        If set to return, the data will be returned as dictionary
        '''

        if (self.proxies != None):
            proxySize = len(self.proxies)
            count = 0

        all_data = {}        


        for coinDetail in self.detailsList:
            self.logger.info("Scraping {} Data".format(coinDetail['coinname']))
            self.logger.info("Starting Year: {} Ending Year: {}".format(coinDetail['start'].year, coinDetail['end'].year))

            if (self.proxies != None):
                proxy = self.proxies[count]
            else:
                proxy = None
            
            start_date_time = coinDetail['start']
            end_date_time = coinDetail['end']
            
            delta = relativedelta(years=1)
            tData = {}
            
            while start_date_time <= end_date_time:
                temp_start=start_date_time

                start_date_time += delta

                temp_end = start_date_time

                if start_date_time > end_date_time:
                    temp_end = end_date_time
                
                if form == "save":
                    self.scrape(temp_start, temp_end, proxy, form, coinDetail['keyword'], coinDetail['coinname'])
                elif form == "return":
                    tData.update(self.scrape(temp_start, temp_end, proxy, form, coinDetail['keyword'], coinDetail['coinname']))

                if (self.proxies != None):
                    count +=1
                    
                    if (count >= proxySize):
                        count = 0
            
            all_data[coinDetail['coinname']] = tData
            
        if form == "return":
            return all_data