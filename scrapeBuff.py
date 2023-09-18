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
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# The notifier function

iconTrue = {
    'src': 'https://i.ibb.co/0sYG97C/checkmark-true.png',
    'placement': 'appLogoOverride'
}

iconFalse = {
    'src': 'https://i.ibb.co/mzWDY0n/checkmark-false.png',
    'placement': 'appLogoOverride'
}


item_found_event = threading.Event()

# Add the following global variables at the beginning of your code
total_page_counter = 0
missed_page_counter = 0
found_page_counter = 0
missed_tag_counter = 0
start_time = None
end_time = None

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('buff-bot-e6cdb8b80af6.json', scope)
client = gspread.authorize(credentials)

# Open the Google Sheet by its title
sheet = client.open('Buff163-Skins').sheet1


# Add this function at the beginning of your script
def check_stop_condition():
    # You can define your own condition to stop the code here
    # For example, you can check for a specific key press, or a signal from an external source
    # For now, let's assume you want to stop after a specific number of pages checked
    global total_page_counter, missed_page_counter, found_page_counter, start_time, end_time, missed_tag_counter
    max_pages_to_check = 500  # Change this to your desired maximum
    # print(f"Total Pages Checked: {total_page_counter}")
    if total_page_counter >= max_pages_to_check:
        print(f"Reached maximum pages to check ({max_pages_to_check}). Stopping...")
        end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Total Pages Checked: {total_page_counter}")
        print(f"Missed Pages: {missed_page_counter}")
        print(f"Missed Tags: {missed_tag_counter}")
        print(f"Found Pages: {found_page_counter}")
        print(f"Start Time: {start_time}")
        print(f"End Time: {end_time}")
        sys.exit()

def notify(title, text, result):
    if (result == True):
        toast(title, text, icon=iconTrue, app_id='Microsoft.WindowsTerminal_8wekyb3d8bbwe!App')
    else:
        toast(title, text, icon=iconFalse, app_id='Microsoft.WindowsTerminal_8wekyb3d8bbwe!App')


def update_found_item_gsheet(url):
    # Define the scope and credentials to access your Google Sheet
    global sheet
    # Find the row index where the link is located
    cell = sheet.find(url)
    row_index = cell.row

    # Get the current value in the "Item Found" column
    current_value = int(sheet.cell(row_index, 9).value)  # Assuming "Item Found" column is in column 8

    # Increment the value by 1 and update the cell
    new_value = current_value + 1
    sheet.update_cell(row_index, 9, new_value)  # Assuming "Item Found" column is in column 8


def getSkinTitle(driver):
    divLocated = 6
    global total_page_counter, missed_page_counter
    total_page_counter += 1
    try:
        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[{}]/div/div[1]/div[2]/div[1]/h1'.format(divLocated))))
        # title = driver.find_element(By.XPATH, '/html/body/div[{}]/div/div[1]/div[2]/div[1]/h1'.format(divLocated)).text
        # print(title)
    except TimeoutException:
        divLocated += 1
        
    if divLocated == 7:
        try: 
            WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[{}]/div/div[1]/div[2]/div[1]/h1'.format(divLocated))))
            # title = driver.find_element(By.XPATH, '/html/body/div[{}]/div/div[1]/div[2]/div[1]/h1'.format(divLocated)).text
            # print(title)
        except TimeoutException:
            divLocated = 0
    if divLocated == 0:
        print('Skin Title Not Found')
        missed_page_counter += 1
        return divLocated
    else:
        # print(driver.find_element(By.XPATH, '/html/body/div[{}]/div/div[1]/div[2]/div[1]/h1'.format(divLocated)).text)
        return divLocated
    
def getSkinTags(driver, divLocated, i):
    global missed_tag_counter
    try:
        price = driver.find_element(By.XPATH, '/html/body/div[{}]/div/div[7]/table/tbody/tr[{}]/td[5]/div[1]/strong'.format(divLocated, i+2))
        wear = driver.find_element(By.XPATH, '/html/body/div[{}]/div/div[7]/table/tbody/tr[{}]/td[3]/div/div[1]/div[1]'.format(divLocated, i+2))
    except NoSuchElementException:
        missed_tag_counter += 1
        print("Tags Not Found for Listing {}".format(i))
        return False, False
    weartext = float(''.join(c for c in wear.text if c.isdigit() or c=='.'))
    price_text = price.text
    # Remove the currency symbol and extra spaces
    price_text = price_text.replace('¥', '').strip()
    # Convert the string to a float
    price_float = float(price_text)
    # print("Listing: {}".format(i))
    # print("Wear: {}".format(weartext))
    # print("Price: {}".format(price_float))
    
    return weartext, price_float

def checkItems(driver, divLocated):
    global missed_tag_counter
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[{}]/div/div[7]/table/tbody/tr[6]/td[3]/div/div[1]/div[1]'.format(divLocated))))
        element = driver.find_element(By.XPATH, '/html/body/div[{}]/div/div[7]/table/tbody/tr[2]/td[3]/div/div[1]/div[1]'.format(divLocated))
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
    except TimeoutException:
        print("Items of Skin Not Found")
        missed_tag_counter += 1
        return False
    return True

def obtainItems(request, driver, maximumFloat, maximumPrice): # obtain list of 10 items wear values and prices for the links found in json file. Returns true if match is found
    global found_page_counter
    divTitle = getSkinTitle(driver)
    
    if divTitle != 0:
        itemsChecked = checkItems(driver, divTitle)
        if itemsChecked == True:
            for i in range(10):
                weartext, price_float = getSkinTags(driver, divTitle, i)
                
                if weartext != False:
                    if weartext < maximumFloat:
                        if price_float < maximumPrice:
                            PurchaseThread(request, i, maximumFloat, maximumPrice, divTitle).start()
                            found_page_counter += 1
                            # update_found_item_gsheet(driver.current_url)

class PurchaseThread(threading.Thread):
    def __init__(self, request, listing, maximumFloat, maximumPrice, divTitle):
        threading.Thread.__init__(self)
        self.request = request
        self.listing = listing
        self.maximumFloat = maximumFloat
        self.maximumPrice = maximumPrice
        self.divTitle = divTitle
    def run(self):
        global item_found_event
        item_found_event.set()
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument("--enable-javascript")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-web-security")
        options.add_argument("--incognito")
        options.add_argument("--disable-cache")

        # Disable images
        prefs = {"profile.managed_default_content_settings.images": 2, "profile.default_content_setting_values.notifications": 2, "profile.managed_default_content_settings.stylesheets": 2}
        options.add_experimental_option("prefs", prefs)

        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)")

        driver = webdriver.Chrome(options=options)
        driver.delete_all_cookies()
        driver.execute_script("window.open('{}', '_blank');".format(self.request))
        
        driver.switch_to.window(driver.window_handles[0])
        driver.close()
        # Switch back to the remaining tab(s)
        driver.switch_to.window(driver.window_handles[0])
        item_found_event.clear()
        purchase(driver, self.request, self.listing, self.maximumFloat, self.maximumPrice, self.divTitle)
        print("Finished Purchase {}".format(self.listing))

class ScrapeThread(threading.Thread):
    def __init__(self, scrapernumber):
        threading.Thread.__init__(self)
        self.scrapernumber = scrapernumber
    def run(self):
        global item_found_event
        scrapeCount = 'scraper' + str(self.scrapernumber)
        links = [product_info['link'] for product_info in data[scrapeCount]]
        maximumPrices = [product_info['price'] for product_info in data[scrapeCount]]
        maximumFloats = [product_info['float'] for product_info in data[scrapeCount]]

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument("--enable-javascript")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-web-security")
        # options.add_argument("--incognito")
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
        
        driver.get('https://buff.163.com/goods/857578')
        
        driver.delete_all_cookies()
        driver.execute_script('window.localStorage.clear();')
        
        randomCookie = random.randint(1, 22)
        cookie_file_path = "./fake_Cookies/{}.pkl".format(randomCookie)
        cookies = pickle.load(open(cookie_file_path, "rb")) 
        
        for cookie in cookies:
            driver.add_cookie(cookie)
            
        driver.refresh()
        time.sleep(1)
        
        for url in links:
            randomNumber = random.uniform(1, 10)
            time.sleep(randomNumber)
            driver.execute_script("window.open('{}', '_blank');".format(url))

        driver.switch_to.window(driver.window_handles[0])
        driver.close()
        # Switch back to the remaining tab(s)
        driver.switch_to.window(driver.window_handles[0])
        
        # driver.delete_all_cookies()
        # driver.execute_script('window.localStorage.clear();')

        # device_id = str(uuid.uuid4())
        # client_id = str(uuid.uuid4())
        # driver.add_cookie({'name': 'deviceId', 'value': device_id})
        # driver.add_cookie({'name': 'client_id', 'value': client_id})
        
        
        tab_order = list(driver.window_handles)  # Save the initial order
        while True:
            # Loop through each tab and refresh
            currentDate = datetime.datetime.now().strftime("%H:%M:%S")
            print("Scraper {} Starting Over at {}".format(self.scrapernumber ,currentDate))
            check_stop_condition()
            for i, handle in enumerate(tab_order):
                # print("Scrape {} Refreshing".format(i))
                driver.switch_to.window(handle)

                if item_found_event.is_set():
                    time.sleep(5)
                    print('Waited for 5 seconds')

                driver.refresh()
                randomNumber2 = random.uniform(3.5, 7.5)
                time.sleep(randomNumber2)
                current_url = driver.current_url
                position = None
                for i, item in enumerate(links):
                    if item == current_url:
                        position = i
                        break
                # Now `position` will contain the position of the current URL in the links list
                # print("Position:", position)
                # print("Current URL:", current_url)
                # print("Maximum Float:", maximumFloats[position])
                # print("Maximum Price:", maximumPrices[position])
                obtainItems(current_url, driver, maximumFloats[position], maximumPrices[position])

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
    
start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
item_found_event.clear()
if (data == None):
    print("No data found")
    pass
else:
    if len(sys.argv) != 3:
        print('Please enter the correct number of arguments')
        pass
    else:
        item_found_event.clear()
        scrape(int(sys.argv[1]), int(sys.argv[2]))

# Note: if you want an example of a function run, uncomment this:
# scrape(1, 4, 0.10)

# add readme.md

# Add this at the very end of your script to print the statistics
end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"Total Pages Checked: {total_page_counter}")
print(f"Missed Pages: {missed_page_counter}")
print(f"Start Time: {start_time}")
print(f"End Time: {end_time}")