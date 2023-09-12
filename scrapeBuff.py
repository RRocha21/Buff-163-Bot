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
import random
import uuid
import datetime

# The notifier function

iconTrue = {
    'src': 'https://i.ibb.co/0sYG97C/checkmark-true.png',
    'placement': 'appLogoOverride'
}

iconFalse = {
    'src': 'https://i.ibb.co/mzWDY0n/checkmark-false.png',
    'placement': 'appLogoOverride'
}

def notify(title, text, result):
    if (result == True):
        toast(title, text, icon=iconTrue, app_id='Microsoft.WindowsTerminal_8wekyb3d8bbwe!App')
    else:
        toast(title, text, icon=iconFalse, app_id='Microsoft.WindowsTerminal_8wekyb3d8bbwe!App')


def getSkinTitle(driver):
    divLocated = 6
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[{}]/div/div[1]/div[2]/div[1]/h1'.format(divLocated))))
    except TimeoutException:
        divLocated += 1
        
    if divLocated == 7:
        try: 
            WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[{}]/div/div[1]/div[2]/div[1]/h1'.format(divLocated))))
        except TimeoutException:
            divLocated == 0
    if divLocated == 0:
        print('Skin Title Not Found')
        return divLocated
    else:
        return divLocated
    
def getSkinTags(driver, divLocated, i):
    try:
        wear = driver.find_element(By.XPATH, '/html/body/div[{}]/div/div[7]/table/tbody/tr[{}]/td[3]/div/div[1]/div[1]'.format(divLocated, i+2))
        price = driver.find_element(By.XPATH, '/html/body/div[{}]/div/div[7]/table/tbody/tr[{}]/td[5]/div[1]/strong'.format(divLocated, i+2)) #consistent html behavior across different item links for CS:GO
    except NoSuchElementException:
        print("Skin Tags Not Found")
        return False, False
    weartext = float(''.join(c for c in wear.text if c.isdigit() or c=='.'))
    price_text = price.text
    # Remove the currency symbol and extra spaces
    price_text = price_text.replace('¥', '').strip()
    # Convert the string to a float
    price_float = float(price_text)
    
    return weartext, price_float

def checkItems(driver, divLocated):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[{}]/div/div[7]/table/tbody/tr[3]/td[5]/div[1]/strong'.format(divLocated))))
    except TimeoutException:
        print("Items of Skin Not Found")
        return False
    return True

def obtainItems(request, driver, maximumFloat, maximumPrice): # obtain list of 10 items wear values and prices for the links found in json file. Returns true if match is found
    driver.delete_all_cookies()
    driver.get(request) # driver configs
    driver.execute_script('window.localStorage.clear();')

    device_id = str(uuid.uuid4())
    driver.add_cookie({'name': 'deviceId', 'value': device_id})
    time.sleep(1)
    driver.refresh()
    time.sleep(1)

    divTitle = getSkinTitle(driver)
        
    if divTitle != 0:
        itemsChecked = checkItems(driver, divTitle)
        if itemsChecked == True:
            for i in range(10):
                weartext, price_float = getSkinTags(driver, divTitle, i)
                
                if weartext != False:
                    if weartext < maximumFloat:
                        if price_float < maximumPrice:
                            print('---------  Found Item  ---------')
                            PurchaseThread(request, i, maximumFloat, maximumPrice, divTitle).start()
    driver.quit()

class PurchaseThread(threading.Thread):
    def __init__(self, request, listing, maximumFloat, maximumPrice, divTitle):
        threading.Thread.__init__(self)
        self.request = request
        self.listing = listing
        self.maximumFloat = maximumFloat
        self.maximumPrice = maximumPrice
        self.divTitle = divTitle
    def run(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument("--enable-javascript")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-web-security")
        options.add_argument("--incognito")
        options.add_argument("--disable-cache")

        # Disable images
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)")
        
        driver = webdriver.Chrome(options=options)
        purchase(driver, self.request, self.listing, self.maximumFloat, self.maximumPrice, self.divTitle)
        print("Finished Purchase {}".format(self.listing))

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
                options.add_argument("--allow-running-insecure-content")
                options.add_argument("--disable-web-security")
                options.add_argument("--incognito")
                options.add_argument("--disable-cache")

                # Disable images
                prefs = {"profile.managed_default_content_settings.images": 2}
                options.add_experimental_option("prefs", prefs)
                
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
    with open('buff2.json', 'r') as f:
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
