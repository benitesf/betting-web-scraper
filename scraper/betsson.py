# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 20:07:49 2023

@author: edzon
"""

import requests

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from scraper import Scraper

import json
import time
import sys

class Bettson(Scraper):
    def __init__():
        pass
    
    def extract(url):
url = 'https://www.betsson.com/pe/apuestas-deportivas/futbol?bte=true&tab=competitionsAndLeagues&eventId=f-eGIT6KdbmEmXxbZsPZpJOw&eti=0&fs=true'
#url = 'https://www.betsson.com/pe/apuestas-deportivas/futbol?eventId=f-Sd3_UV2wBUKqQvJJUT4tNQ&tab=competitionsAndLeagues&eti=0&fs=true&mtg=3'

options = Options()
options.add_argument('--headless=new')
options.add_argument('start-maximized')
options.add_argument('disable-infobars')
options.add_argument('--disable-extensions')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                          options=options)
driver.get(url)
driver.implicitly_wait(3)

# Get match football team's name
teams = driver.find_elements(By.XPATH, "//div[@test-id='event-page.participants']//span[@class='ng-star-inserted']")
match_name = teams[0].text + ' vs ' + teams[1].text

# Get active bet option
# url + &mtg=[bet_ops_cod]
soup = BeautifulSoup(driver.page_source, "lxml")
mtg_elements = soup.select("obg-tabs.obg-tabs.ng-star-inserted div.obg-tabs-content.ng-star-inserted obg-tab-label.obg-tab-label.ng-star-inserted")
mtg_list = {}

#for i in range(4, len(mtg_elements)):
for i in range(4, 5):
    try:
        element = mtg_elements[i].select("div.ng-star-inserted span.ng-star-inserted")[0]
        mtg_name = element.text
        mtg_id = int(mtg_elements[i]['test-id'])
        mtg_list[mtg_id] = mtg_name
    except:
        print(f"Error in position {i}")

match_betting = {}

# Iterate over each mtg id
for mtg_id, mtg_name in mtg_list.items():
    driver.get(url + f"&mtg={mtg_id}")
    driver.implicitly_wait(3)
    
    #active = driver.find_element(By.XPATH, "//div[@class='obg-tabs-content ng-star-inserted']//obg-tab-label[@class='obg-tab-label ng-star-inserted active']//div[@class='ng-star-inserted']//span[@class='ng-star-inserted']").text        
    market = {}
    
    # Scrolling
    wait = WebDriverWait(driver, 0.3)
    i = 0
    j = 1000
    
    while i < j:
        try:
            element = wait.until(EC.visibility_of_element_located((By.XPATH, f"//div[@test-id='{i}']")))
            element.location_once_scrolled_into_view        
            time.sleep(0.2)
            
            try:
                s = driver.find_element(By.XPATH, f"//div[@test-id='{i}']//span[@test-id='odds']").text            
            except:
                driver.find_element(By.XPATH, f"//div[@test-id='{i}']//span[@class='ico-chevron-down obg-m-event-market-group-toggle-icon']").click()
                #print("Expanded")
            
            # Extract item header
            header = driver.find_element(By.XPATH, f"//div[@test-id='{i}']//span[@class='obg-m-event-market-group-header-name ng-star-inserted']").text
            # Extract odds
            odd_elements = driver.find_elements(By.XPATH, f"//div[@test-id='{i}']//obg-selection-container[@test-id='event.market-selection']")
            odds_dict = {}
            for odd in odd_elements:
                odd_name = odd.find_element(By.XPATH, ".//div[@class='obg-selection-content-label-wrapper']//span[@class='obg-selection-content-label ng-star-inserted']").text
                odd_value = odd.find_element(By.XPATH, ".//obg-numeric-change[@class='obg-numeric-change ng-star-inserted']//span[@test-id='odds']").text
                odds_dict[odd_name] = odd_value
                
            market[header] = odds_dict    
            i += 1
        except:        
            break
    
    # Get all match betting sections
    match_betting[mtg_name] = market
    
# Save to json file
json_object = json.dumps(match_betting, indent=4, ensure_ascii=False)
        
# Quit browser
driver.quit()