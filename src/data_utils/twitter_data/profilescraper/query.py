from multiprocessing.pool import Pool
import requests
import json
import random
import time

from functools import partial

from libs.writing_utils import get_logger, get_locations

from profilescraper.profile import Profile

import pandas as pd
import os

class profileScraper:
    def __init__(self, proxy=None, logger=None):
        self.HEADERS_LIST = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0', 'Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0']
        self.proxy = proxy
        _, self.currRoot = get_locations()

        if logger == None:
            self.logger = get_logger(os.path.join(self.currRoot, "logs/profilescraper.log"))
        else:
            self.logger = logger

    def query_single_profile(self, url, retry=10):
        self.logger.info("Querying {}".format(url))
        
        headers = {'User-Agent': random.choice(self.HEADERS_LIST)}

        try:
            if (self.proxy == None):
                response = requests.get(url, headers=headers)
            else:
                response = requests.get(url, headers=headers, proxies=self.proxy)

            html = response.text or ''

            profile = Profile.from_html(html)

            if not profile:
                return 0

            return profile
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
            return self.query_single_profile(url, retry-1)
        
        self.logger.error("Giving up.")
        return 0


    def query_profile(self, profiles, poolsize=20):
        '''
        profiles: List
        Unique profies to scrape from

        poolsize: int
        Size of pool. Bigger - the more instance of browser is opened

        logger (logger):
        Made this mandatory here because of issues
        '''

        url = "https://twitter.com/{}"
        no_profiles = len(profiles)

        if (poolsize > no_profiles):
            poolsize = no_profiles

        urls = [url.format(x) for x in profiles]
        all_profile = []

        pool = Pool(poolsize)

        try:
            for profile_data in pool.imap_unordered(partial(self.query_single_profile), urls):
                all_profile.append(profile_data)
                self.logger.info("Got {} profiles (1 new).".format(len(all_profile)))

        finally:
            pool.close()
            pool.join()

        return all_profile
    
class query_historic_profiles():
    def __init__(self, profiles, proxies=None, relative_dir=""):
        '''
        Functions to call to save historic profiles

        Parameters:
        __________
        profiles (Pandas Series or list or numpy):
        Series of profile name
        '''

        self.profiles = profiles
        _, self.currRoot = get_locations()

        self.logger = get_logger(os.path.join(self.currRoot, "logs/query_profile.log"))
        
        self.path = os.path.join(self.currRoot, relative_dir, "data/profile")
        self.proxies = proxies

    def scrape_list(self, currList, poolsize, proxy, count):
        '''
        Calls the scraper
        '''
        if (len(currList) > 0):
            ps = profileScraper(proxy)
            profiles = ps.query_profile(currList, poolsize=poolsize)
            self.profiles_to_pandas(profiles)

            count += 1

        return count

    def profiles_to_pandas(self, profiles):
        userDf = pd.DataFrame(columns=['username', 'location', 'has_location', 'created', 'is_verified', 'total_tweets', 'total_following', 'total_followers', 'total_likes', 'has_avatar', 'has_background', 'is_protected', 'profile_modified'])
        tweetDf = pd.DataFrame(columns=['User', 'ID', 'Tweet', 'Time', 'Likes', 'Replies', 'Retweet'])

        for profile in profiles:   
            for tweet in profile.tweets:
                tweetDf = tweetDf.append({'User': profile.username, 'ID': tweet.id, 'Tweet': tweet.text, 'Time': tweet.timestamp, 'Likes': tweet.likes, 'Replies': tweet.replies, 'Retweet': tweet.retweets}, ignore_index=True)

            userDf = userDf.append({'username':profile.username, 'location':profile.location, 'has_location':profile.has_location, 'created':profile.created, 'is_verified':profile.is_verified, 'total_tweets':profile.total_tweets, 'total_following':profile.total_following, 'total_followers':profile.total_followers, 'total_likes':profile.total_likes, 'has_avatar':profile.has_avatar, 'has_background':profile.has_background, 'is_protected':profile.is_protected, 'profile_modified':profile.profile_modified}, ignore_index=True)

        tweetDf = tweetDf.to_csv(os.path.join(self.path, 'live/userTweets.csv'), index=None, mode='a')
        userDf.to_csv(os.path.join(self.path, 'live/userData.csv'), index=None, mode='a')
        userDf['username'].to_csv(os.path.join(self.path, 'live/extractedUsers.csv'), index=None, mode='a')

        self.logger.info("Saved to userTweets.csv and extractedUsers.csv")

    def perform_search(self, poolsize=20):
        '''
        The function to call by other classes in order to search for profiles

        Parameters:
        __________
        poolsize (int) (optional):
        The size of pool
        '''

        if (self.proxies == None):
            proxySize = 10
        else:
            proxySize = len(self.proxies)

        try:
            alreadyRead = pd.read_csv(os.path.join(self.path, 'extractedUsers.csv'), header=None)[0]
        except:
            self.logger.info("Already extracted users not found - Starting from a clean slate")

            try:
                os.remove(os.path.join(self.path, "extractedUsers.csv"))
            except:
                pass

            os.mknod(os.path.join(self.path, "extractedUsers.csv"))
            alreadyRead = pd.Series()

        #set profiles value by reading the csv file

        uniqueUsers = list(set(self.profiles) - set(alreadyRead))

        self.logger.info("File contains {} data. Scraping for {} after cache".format(len(self.profiles), len(uniqueUsers)))

        oldi = 0
        count = 0

        for i in range(0, len(uniqueUsers), poolsize*5):
            if (self.proxies == None):
                currProxy = None
            else:
                currProxy = self.proxies[count]

            count = self.scrape_list(uniqueUsers[oldi:i], poolsize=poolsize, proxy=currProxy, count=count)

            if (count >= proxySize):
                count = 0

            self.logger.info("Done {} of {}".format(i, len(uniqueUsers)))
            oldi = i
        
        if (len(uniqueUsers) == 0):
            pass
        else:
            self.scrape_list(uniqueUsers[i:], poolsize=poolsize, proxy=None, count=count)