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
import numpy as np

import time

url ="https://www.tradingview.com"
driver = webdriver.Remote(
command_executor='http://127.0.0.1:4444/wd/hub',
desired_capabilities=DesiredCapabilities.CHROME)

driver.set_window_size(1366, 768)

driver.find_elements_by_xpath("//a[contains(text(),'Sign In')]")[1].click()


driver.find_element_by_name('username').send_keys('bame4')
driver.find_element_by_name('password').send_keys('quantorithm123')

driver.find_element_by_tag_name('body').send_keys(Keys.ENTER)


def scrape(cname, stop_point):
    info = soup.find_all( "div", class_="tv-site-widget tv-widget-idea js-widget-idea")
    df = pd.DataFrame(columns=['Time Stamp', 'Username', 'Topic', 'Text', 'Direction', 'Views', 'Cmt.Num', 'Like'])
    
    loopout = 0

    for i in range(1, pagenum+1):
        url1 = "https://www.tradingview.com/symbols/{}/page-{}/?sort=recent".format(cname, i)
   
        if i != 1:
            driver.get(url1)

        for data in info:
            user = data.find('img')['alt']
            topic = data.find(class_="tv-widget-idea__title-name apply-overflow-tooltip").get_text()
            link = 'https://tradingview.com' + data.find(class_='js-widget-idea__popup')['data-href-idea-custom-link']
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

            dec = 'https://tradingview.com' + data.find(class_='js-widget-idea__popup')['data-href-idea-custom-link']
            print(dec)

            driver.get(dec)
            soup1=BeautifulSoup(driver.page_source, 'lxml')

            text = soup1.find(class_="tv-chart-view__description-wrap js-chart-view__description").get_text()

            df = df.append({'Time Stamp':time, 'Username':user, 'Topic':topic, 'Text':text, 'Views':views, 'Direction':direction,       'Cmt.Num':com, 'Like':lik}, ignore_index=True)      
            time=float(time)
            stop_point=float(stop_point)
            
            print(time)
            print(stop_point)
            
            if (time <= stop_point):
                loopout = 1
                break
                
            df.to_csv('live/temp.csv')
            driver.back()
    
        if (loopout == 1):
            break

    return df

coinname = {'BTCUSD', 'LTCUSD', 'ETHUSD', 'DASHUSD', 'STRUSD', 'DOGEUSD', 'XRPUSD', 'XMRUSD'}


for key in coinname:

    live = pd.read_csv('data/{}.csv'.format(key), engine="python")
    live = live.sort_values('Time Stamp').reset_index(drop=True)
    live['Time Stamp'] = live['Time Stamp'].astype(int)
    largest = live.iloc[-1]['Time Stamp']
    
    stop_point = largest
    

    driver.get("https://www.tradingview.com/symbols/{}/?sort=recent".format(key))
    #Selenium hands the page source to Beautiful Soup
    soup=BeautifulSoup(driver.page_source, 'lxml')

    page = soup.find(class_="tv-load-more__pagination js-feed-pagination")

    lastp = soup.find_all(class_="tv-load-more__page")

    pagenum = int(lastp[-1].get_text())
    
    
    df = scrape(key, stop_point)
    df.to_csv("data/{}.csv".format(key), mode='a', header=False)

driver.close()