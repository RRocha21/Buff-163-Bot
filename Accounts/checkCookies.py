#Note: Buff163 does not release its statistics on rate limits, but upon testing, a total of 3 scrapers at a time works best
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
# from executeOrder import purchase
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
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# The notifier function

class ScrapeThread(threading.Thread):
    def __init__(self, scrapernumber):
        threading.Thread.__init__(self)
        self.scrapernumber = scrapernumber
    def run(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument("--enable-javascript")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-web-security")
        options.add_argument("--incognito")
        options.add_argument("--disable-cache")

        # # Disable images
        prefs = {"profile.managed_default_content_settings.images": 2, "profile.default_content_setting_values.notifications": 2, "profile.managed_default_content_settings.stylesheets": 2}
        options.add_experimental_option("prefs", prefs)

        if self.scrapernumber == 1:
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/93.0.961.44 Safari/537.36")
        elif self.scrapernumber == 2:
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36")
        elif self.scrapernumber == 3:
            options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36")
        elif self.scrapernumber == 4:
            options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.44")
        elif self.scrapernumber == 5:
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/93.0.961.44 Safari/537.36")
        elif self.scrapernumber == 6:
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/93.0.961.44 Safari/537.36 ")

        driver = webdriver.Chrome(options=options)
        driver.delete_all_cookies()
        
        
        for i in range(0, 33):
            randomNumber = random.uniform(1, 2)
            time.sleep(randomNumber)
            driver.execute_script("window.open('{}', '_blank');".format('https://buff.163.com/goods/781592'))

        driver.switch_to.window(driver.window_handles[0])
        driver.close()
        # Switch back to the remaining tab(s)
        driver.switch_to.window(driver.window_handles[0])
        
        
        tab_order = list(driver.window_handles)  # Save the initial order
        randomCookie = 0
        while True:
            # Loop through each tab and refresh
            currentDate = datetime.datetime.now().strftime("%H:%M:%S")
            print("Scraper {} Starting Over at {}".format(self.scrapernumber ,currentDate))
            if randomCookie > 33:
                break;
            for i, handle in enumerate(tab_order):
                # print("Scrape {} Refreshing".format(i))
                driver.switch_to.window(handle)
                try: 
                    driver.delete_all_cookies()
                    driver.execute_script('window.localStorage.clear();')
                    randomCookie = randomCookie + 1
                    cookie_file_path = "../fake_Cookies/{}.pkl".format(randomCookie)
                    cookies = pickle.load(open(cookie_file_path, "rb")) # enable cookies
                    for cookie in cookies:
                        driver.add_cookie(cookie)
                    device_id = str(uuid.uuid4())
                    client_id = str(uuid.uuid4())
                    driver.add_cookie({'name': 'deviceId', 'value': device_id})
                    driver.add_cookie({'name': 'client_id', 'value': client_id})
                    time.sleep(0.5)
                except Exception as e:
                    print('Could not add cookies')

                try:
                    driver.refresh()
                except Exception as e:
                    print('Could not refresh')
                driver.refresh()
                time.sleep(10)

                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[6]/div/div[7]/table/tbody/tr[2]/td[3]/div/div[1]/div[1]')))
                    try:
                        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[3]/ul/li[1]/a')))
                        element = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[3]/ul/li[1]/a').text
                        if element == '登录/注册':
                            print("Cookie {} Expired".format(randomCookie))
                            pass
                        elif element == 'Login/Registrar':
                            print("Cookie {} Expired".format(randomCookie))
                            pass
                        elif element == 'Login/Register':
                            print("Cookie {} Expired".format(randomCookie))
                            pass
                        else:
                            print("Cookie {} Valid".format(randomCookie))
                            pass
                    except TimeoutException:
                        print("Cookie {} Did Not Found Login Status".format(randomCookie))
                        pass
                except TimeoutException:
                    try: 
                        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[6]/div/div[7]/table/tbody/tr[2]/td[3]/div/div[1]/div[1]')))
                        try:
                            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[3]/ul/li[1]/a')))
                            element = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[3]/ul/li[1]/a').text
                            if element == '登录/注册':
                                print("Cookie {} Expired".format(randomCookie))
                                pass
                            elif element == 'Login/Registrar':
                                print("Cookie {} Expired".format(randomCookie))
                                pass
                            elif element == 'Login/Register':
                                print("Cookie {} Expired".format(randomCookie))
                                pass
                            else:
                                print("Cookie {} Valid".format(randomCookie))
                                pass
                        except TimeoutException:
                            print("Cookie {} Did Not Found Login Status".format(randomCookie))
                            pass
                    except TimeoutException:
                        print("Cookie {} Failed".format(randomCookie))
                        pass

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
    with open('../buff.json', 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    print("File not found")
except json.decoder.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
    
start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

# Add this at the very end of your script to print the statistics
end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")