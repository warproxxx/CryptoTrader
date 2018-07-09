from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from IPython.display import Image
from IPython.core.display import HTML 

import getpass

from bs4 import BeautifulSoup, Comment
import re
import pandas as pd
import os
import os.path
import numpy as np

import uuid

import time
from datetime import datetime

import uuid
import logging

class manage():

    def __init__(self):
        logging.basicConfig(filename=__file__.replace('tradingviewManger.py', 'logs.txt'),level=logging.INFO)
        self.currentDir = __file__.replace('tradingviewManger.py', '')
        
        url ="https://www.tradingview.com/"
        
        self.driver = webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub', desired_capabilities=DesiredCapabilities.CHROME)
        
        self.driver.set_window_size(1366, 768)
        self.driver.get(url)
        
        attempts = 0
        
        while attempts < 3:
            try:
                self.driver.find_elements_by_xpath("//a[contains(text(),'Sign In')]")[1].click() #can directly goto signin URL  
                self.save_screenshot()
                break
            except:
                logging.warning("Error clicking sign in. Trying again")
                attempts = attempts + 1
                
                if (attempts > 2):
                    logging.error("Failed to login even after 3 attempts")
                    self.driver.close()
                    sys.exit()
        
        self.driver.find_element_by_name('username').send_keys('bame4')
        self.driver.find_element_by_name('password').send_keys('quantorithm123')
        self.save_screenshot()
        
        self.driver.find_element_by_tag_name('body').send_keys(Keys.ENTER)
        
        logging.info("Login Completed at {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.save_screenshot()
    
    def save_screenshot(self, fName=datetime.now().strftime('%Y-%m-%d %H:%M:%S')):
        fullDir = self.currentDir+'data/image/{}.png'.format(fName)
        self.driver.save_screenshot(fullDir)

        
        
    def scrape(self, cname, stop_point):
        info = self.soup.find_all( "div", class_="tv-site-widget tv-widget-idea js-widget-idea")
        df = pd.DataFrame(columns=['Time Stamp', 'Username', 'Topic', 'Text', 'Direction', 'Views', 'Cmt.Num', 'Like'])
        
        loopout = 0
        
        savingFile = self.currentDir + 'data/live/temp-{}-{}.csv'.format(cname, uuid.uuid4().hex[:10].upper())

        for i in range(1, self.pagenum+1):
            url1 = "https://www.tradingview.com/symbols/{}/page-{}/?sort=recent".format(cname, i)
            self.save_screenshot()
            
            if i != 1:
                self.driver.get(url1)

            for data in info:
                user = data.find('img')['alt']
                topic = data.find(class_="tv-widget-idea__title-name apply-overflow-tooltip").get_text()
                
                
                link = 'https://tradingview.com' + data.find(class_='js-widget-idea__popup')['href']
                views = data.find(class_="tv-social-stats__count").get_text()
                time = data.find(class_="tv-widget-idea__time")['data-timestamp']
                like = data.find_all(class_="tv-social-stats__count")
                com = like[1].get_text()
                lik =like[2].get_text()
                direction = data.find(class_="tv-idea-label tv-idea-label--long i-except-phones-only")
                
                try:
                    direction = direction.get_text()
                except:
                    try:
                        direction = data.find(class_="tv-idea-label tv-idea-label--short i-except-phones-only")
                        direction = direction.get_text()
                    except:
                        pass

                dec = 'https://tradingview.com' + data.find(class_='js-widget-idea__popup')['href']
                logging.info("Opening this link {}".format(dec))
                
                self.driver.get(dec)
                
                soup1=BeautifulSoup(self.driver.page_source, 'lxml')
                text = soup1.find(class_="tv-chart-view__description-wrap js-chart-view__description").get_text()

                df = df.append({'Time Stamp':time, 'Username':user, 'Topic':topic, 'Text':text, 'Views':views, 'Direction':direction, 'Cmt.Num':com, 'Like':lik}, ignore_index=True)      
                time=float(time)
                stop_point=float(stop_point)
                
                logging.info("The Starting Time is : {}".format(time))
               
                if (time <= stop_point):
                    loopout = 1
                    break
                
                df.to_csv(savingFile, index=None)
                self.save_screenshot()
                
                self.driver.back()
                logging.info("Back clicked. The URL is now: {}. URL1 is: {}".format(self.driver.current_url, url1))

            if (loopout == 1):
                break
        
        return savingFile
    
    def download(self):
      
        coinname = {'BTCUSD', 'LTCUSD', 'ETHUSD', 'DASHUSD', 'STRUSD', 'DOGEUSD', 'XRPUSD', 'XMRUSD'}
        
        for key in coinname:
            
            if (os.path.isfile(self.currentDir + 'data/fulldata/{}.csv'.format(key))):
                live = pd.read_csv(self.currentDir + 'data/fulldata/{}.csv'.format(key), engine="python")
                live = live.sort_values('Time Stamp').reset_index(drop=True)
                live['Time Stamp'] = live['Time Stamp'].astype(int)
                largest = live.iloc[-1]['Time Stamp']
            else:
                largest = 0

            stop_point = largest
            
            self.driver.get("https://www.tradingview.com/symbols/{}/?sort=recent".format(key))
            #Selenium hands the page source to Beautiful Soup
            
            self.save_screenshot()
            
            self.soup=BeautifulSoup(self.driver.page_source, 'lxml')

            page = self.soup.find(class_="tv-load-more__pagination js-feed-pagination")

            lastp = self.soup.find_all(class_="tv-load-more__page")

            self.pagenum = int(lastp[-1].get_text())


            fName = self.scrape(key, stop_point)
            df = pd.read_csv(fName)
            
            df['Time Stamp'] = df['Time Stamp'].astype(np.int64)
            
            df = df.sort_values('Time Stamp').reset_index(drop=True)
 
            if (largest == 0):
                df.to_csv(self.currentDir + "data/fulldata/{}.csv".format(key), index=None)
            else:
                df.to_csv(self.currentDir + "data/fulldata/{}.csv".format(key), header=False, mode='a', index=None)
 
            logging.info("Written to {}.csv".format(key))