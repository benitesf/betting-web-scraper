# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import json
import time
import sys


url = 'https://www.betsson.com/pe/apuestas-deportivas/buscar?eventId=f-wvYOM0drCEa2Ivzrk-2wBQ&eti=0&fs=true'
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
match_container_str = "//div[@test-id='event-page.participants']//span[@class='ng-star-inserted']"
match_container = driver.find_elements(By.XPATH, match_container_str)
local = match_container[0].text
visit = match_container[1].text

print("#########################")
print("Local: " + local)
print("Visita: " + visit)
print("#########################\n\n")

soup = BeautifulSoup(driver.page_source, "lxml")

# Get betting markets
# url + &mtg=[bet_ops_cod]
market_container_str = "div.obg-m-event-market-tabs-tab-container obg-tab-label"
market_container = soup.select(market_container_str)
print("nº markets: " + str(len(market_container)))
markets = {}

market_name_container_str = "div.ng-star-inserted span.label-text"

for i in range(4, len(market_container)):
    try:
        market_name = market_container[i].select(market_name_container_str)[0].text        
        market_id = int(market_container[i]['test-id'])
        markets[market_id] = market_name
    except Exception:        
        print(f"Error in position {i}")

print(markets)

match_odds = {}
# markets = {4: "Goles"}

# Iterate over markets
for market_id, market_name in markets.items():
    print(f"\nMarket: {market_name}")
    
    driver.get(url + f"&mtg={market_id}")
    driver.implicitly_wait(3)
    
    #active = driver.find_element(By.XPATH, "//div[@class='obg-tabs-content ng-star-inserted']//obg-tab-label[@class='obg-tab-label ng-star-inserted active']//div[@class='ng-star-inserted']//span[@class='ng-star-inserted']").text        
    market_odds = {}
    
    # Scrolling
    wait = WebDriverWait(driver, 0.3)
    i = 0
    j = 1000
    
    while i < j:
        try:
            element = wait.until(EC.visibility_of_element_located((By.XPATH, f"//div[@test-id='{i}']")))
            element.location_once_scrolled_into_view
            # time.sleep(0.2)
            
            try:
                s = driver.find_element(By.XPATH, f"//div[@test-id='{i}']//span[@test-id='odds']").text            
            except Exception:
                print(f"Expanding...")
                driver.find_element(By.XPATH, f"//div[@test-id='{i}']//span[@class='ico-chevron-down obg-m-event-market-group-toggle-icon']").click()
                time.sleep(0.1)
            
            # Extract item header
            try:
                try:
                    odd_header = driver.find_element(By.XPATH, f"//div[@test-id='{i}']//span[@class='obg-m-event-market-group-header-name ng-star-inserted']").text
                except Exception:
                    print("[INF] Looking for submarkets header")
                    odd_header = driver.find_element(By.XPATH, f"//div[@test-id='{i}']//span[@class='obg-m-event-market-submarkets-group-header-name']").text
            except Exception:
                print(f"[ERR] Header not found. id: {i}")
                break
            
            # Extract odds
            try:
                odds_container = driver.find_elements(By.XPATH, f"//div[@test-id='{i}']//obg-selection-container[@test-id='event.market-selection']")
            except Exception:
                print(f"[ERR] Container not found. id: {i}")
                break
            
            odds = {}
            for odd in odds_container:
                try:
                    odd_name = odd.find_element(By.XPATH, ".//div[@class='obg-selection-content-label-wrapper']//span[@class='obg-selection-content-label ng-star-inserted']").text
                except Exception:
                    print(f"[ERR] Odd name not found. id: {i}")
                    break
                try:
                    odd_value = odd.find_element(By.XPATH, ".//obg-numeric-change[@class='obg-numeric-change ng-star-inserted']//span[@test-id='odds']").text
                except Exception:
                    print(f"[ERR] Odds not found. id: {i}")
                    break
                odds[odd_name] = odd_value
                
            market_odds[odd_header] = odds
            i += 1
        except Exception as ex:
            print(ex)
            print("No more odds..")
            break
    
    match_odds[market_name] = market_odds

# Quit browser
driver.quit()

# Serialize json
json_object = json.dumps(match_odds, indent=4, ensure_ascii=False)

# Save to json file
filename = local + "_vs_" + visit + ".json"
with open("./data/raw/" + filename, "w") as outfile:
    outfile.write(json_object)
