#Note: Buff163 does not release its statistics on rate limits, but upon testing, a total of 3 scrapers at a time works best
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from executeOrder import purchase
from selenium.webdriver.common.keys import Keys
import json
import time
import re
import os
import threading
import pickle
import sys
from win11toast import toast
from selenium.common.exceptions import TimeoutException

# The notifier function

def obtainItems(request, driver, maximumFloat, maximumPrice): # obtain list of 10 items wear values and prices for the links found in json file. Returns true if match is found
    
    driver.delete_all_cookies()
    driver.get(request) # driver configs
    driver.execute_script('window.localStorage.clear();')
    
    cookies = pickle.load(open("cookies.pkl", "rb")) # enable cookies
    for cookie in cookies:
        driver.add_cookie(cookie)
    
    driver.refresh()
    time.sleep(1)
    isNamed = True

    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[7]/div/div[1]/div[2]/div[1]/h1')))
        print(driver.find_element(By.XPATH, '/html/body/div[7]/div/div[1]/div[2]/div[1]/h1').text,':\n')
    except NoSuchElementException:
        print('pass')
        isNamed = False
    except TimeoutException:
        print('Loading took too much time!')
        isNamed = False
        
    if isNamed == True:
        for i in range(10):
            try:
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[7]/div/div[7]/table/tbody/tr[5]/td[3]/div/div[1]/div[1]')))
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[7]/div/div[7]/table/tbody/tr[5]/td[5]/div[1]/strong')))
                wear = driver.find_element(By.XPATH, '/html/body/div[7]/div/div[7]/table/tbody/tr[{}]/td[3]/div/div[1]/div[1]'.format(i+2))
                price = driver.find_element(By.XPATH, '/html/body/div[7]/div/div[7]/table/tbody/tr[{}]/td[5]/div[1]/strong'.format(i+2)) #consistent html behavior across different item links for CS:GO
            except NoSuchElementException:
                print("could not locate item")
                continue
            except TimeoutException:
                print("Loading took too much time!")
                continue
            
            weartext = float(''.join(c for c in wear.text if c.isdigit() or c=='.'))
            price_text = price.text
            # Remove the currency symbol and extra spaces
            price_text = price_text.replace('¥', '').strip()
            # Convert the string to a float
            price_float = float(price_text)
            
            print("Listing {}".format(i+1))
            print("     Price:", price_float)
            print("     Float:", weartext)
            
            if weartext < maximumFloat:
                if price_float < maximumPrice:
                    purchase(driver, i) # This already has 5 second sleep in it
                    driver.refresh()
                    time.sleep(1)
                else:
                    print("         Price is too high")
            else:
                print("         Wear is too high")
    driver.quit()

class ScrapeThread(threading.Thread):
    def __init__(self, scrapernumber):
        threading.Thread.__init__(self)
        self.scrapernumber = scrapernumber
    def run(self):
        scrapeCount = 'scraper' + str(self.scrapernumber)
        while True:
            for link_info in data[scrapeCount]:
                link = link_info['link']
                maximumFloat = link_info['float']
                maximumPrice = link_info['price']
                
                options = webdriver.ChromeOptions()
                options.add_argument('--headless')
                options.add_argument("--enable-javascript")
                options.add_argument("--incognito")
                options.add_argument("--disable-cache")
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36")
                
                driver = webdriver.Chrome(options=options)
                obtainItems(link, driver, maximumFloat, maximumPrice)

def scrape(firstScraper, lastScraper):
    threads = []

    for scrapeNum in range(firstScraper, lastScraper+1):
        t = ScrapeThread(scrapeNum)
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()

data = None

try:
    with open('buff1.json', 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    print("File not found")
except json.decoder.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")

if (data == None):
    print("No data found")
    pass
else:
    if len(sys.argv) != 3:
        print('Please enter the correct number of arguments')
        pass
    else:
        scrape(int(sys.argv[1]), int(sys.argv[2]))

# Note: if you want an example of a function run, uncomment this:
# scrape(1, 4, 0.10)

# add readme.md
