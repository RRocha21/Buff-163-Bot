from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
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
import gspread
from oauth2client.service_account import ServiceAccountCredentials


iconTrue = {
    'src': 'https://i.ibb.co/0sYG97C/checkmark-true.png',
    'placement': 'appLogoOverride'
}

iconFalse = {
    'src': 'https://i.ibb.co/mzWDY0n/checkmark-false.png',
    'placement': 'appLogoOverride'
}

# The notifier function
def notify(title, text, result):
    if (result == True):
        toast(title, text, icon=iconTrue, app_id='Microsoft.WindowsTerminal_8wekyb3d8bbwe!App')
    else:
        toast(title, text, icon=iconFalse, app_id='Microsoft.WindowsTerminal_8wekyb3d8bbwe!App')
        
def update_bought_item_gsheet(url):
    # Define the scope and credentials to access your Google Sheet
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('buff-bot-e6cdb8b80af6.json', scope)
    client = gspread.authorize(credentials)

    # Open the Google Sheet by its title
    sheet = client.open('Buff163-Skins').sheet1
    # Find the row index where the link is located
    cell = sheet.find(url)
    row_index = cell.row

    # Get the current value in the "Item Found" column
    current_value = int(sheet.cell(row_index, 10).value)  # Assuming "Item Found" column is in column 8

    # Increment the value by 1 and update the cell
    new_value = current_value + 1
    sheet.update_cell(row_index, 10, new_value)  # Assuming "Item Found" column is in column 8
        
def initPurchase(driver, request):
    # driver.delete_all_cookies()
    
    # cookies = pickle.load(open("cookies.pkl", "rb")) # enable cookies
    # for cookie in cookies:
    #     driver.add_cookie(cookie)

    driver.refresh()
    time.sleep(1)
    
    
def checkListing(driver, listing, maximumFloat, maximumPrice, divLocated):
    listingStatus = False
    isNamed = True
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[{}]/div/div[1]/div[2]/div[1]/h1'.format(divLocated))))
    except NoSuchElementException:
        notify("FAILED: BUFF 163 BOT", "Page Not Loaded", False)
        isNamed = False
    except TimeoutException:
        isNamed = False
        
    if isNamed == False:
        try: 
            driver.refresh()
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[{}]/div/div[1]/div[2]/div[1]/h1'.format(divLocated))))
            title = driver.find_element(By.XPATH, '/html/body/div[{}]/div/div[1]/div[2]/div[1]/h1'.format(divLocated))
        except NoSuchElementException:
            notify("FAILED: BUFF 163 BOT", "Page Not Loaded", False)
            isNamed = False
        except TimeoutException:
            notify("FAILED: BUFF 163 BOT", "Page Not Loaded", False)
            isNamed = False
            
    if isNamed == True:
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[{}]/div/div[7]/table/tbody/tr[{}]/td[3]/div/div[1]/div[1]'.format(divLocated, listing))))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[{}]/div/div[7]/table/tbody/tr[{}]/td[5]/div[1]/strong'.format(divLocated, listing))))
            wear = driver.find_element(By.XPATH, '/html/body/div[{}]/div/div[7]/table/tbody/tr[{}]/td[3]/div/div[1]/div[1]'.format(divLocated, listing))
            price = driver.find_element(By.XPATH, '/html/body/div[{}]/div/div[7]/table/tbody/tr[{}]/td[5]/div[1]/strong'.format(divLocated, listing)) #consistent html behavior across different item links for CS:GO
        except NoSuchElementException:
            notify("FAILED: BUFF 163 BOT", "Items Not Loaded", False)
            return False
        except TimeoutException:
            notify("FAILED: BUFF 163 BOT", "Items Not Loaded", False)
            return False
    
        weartext = float(''.join(c for c in wear.text if c.isdigit() or c=='.'))
        
        price_text = price.text
        price_text = price_text.replace('¥', '').strip()
        price_float = float(price_text)
        # print("Listing {}".format(listing+1))
        # print("     Price:", price_float)
        # print("     Float:", weartext)
        if weartext < maximumFloat:
            if price_float < maximumPrice:
                listingStatus = True
        return listingStatus
    return False

def clickToBeginPurchase(driver, listing, divLocated):
    try:
        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[{}]/div/div[7]/table/tbody/tr[{}]/td[6]/a'.format(divLocated, listing))))
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        element.click()
        return True
    except TimeoutException:
        notify("FAILED: BUFF 163 BOT", "Div for Purchase Not Found", False)

def clickToPurchase(driver):
    divLocated = 28
    try:
        element = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[{}]/div[2]/div[4]/a'.format(divLocated))))
    except TimeoutException:
        divLocated -= 1
    if divLocated == 27:
        try:
            element = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[{}]/div[2]/div[4]/a'.format(divLocated))))
        except TimeoutException:
            divLocated -= 1
    if divLocated == 26:
        try:
            element = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[{}]/div[2]/div[4]/a'.format(divLocated))))
        except TimeoutException:
            divLocated -= 1
    if divLocated == 25:
        try:
            element = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[{}]/div[2]/div[4]/a'.format(divLocated))))
        except TimeoutException:
            divLocated == 0
    if divLocated == 0:
        notify("FAILED: BUFF 163 BOT", "Purchase Pop Up Not Found", False)
        return False
    else:
        element.click()
        return True
    
def clickToSendProposal(driver):
    divLocated = 30
    try:
        element = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[{}]/div[2]/div/div[2]/a'.format(divLocated))))
    except TimeoutException:
        divLocated -= 1
    if divLocated == 29:
        try:
            element = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[{}]/div[2]/div/div[2]/a'.format(divLocated))))
        except TimeoutException:
            divLocated -= 1
    if divLocated == 28:
        try:
            element = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[{}]/div[2]/div/div[2]/a'.format(divLocated))))
        except TimeoutException:
            divLocated -= 1
    if divLocated == 27:
        try:
            element = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[{}]/div[2]/div/div[2]/a'.format(divLocated))))
        except TimeoutException:
            divLocated = 0
    if divLocated == 0:
        notify("FAILED: BUFF 163 BOT", "Proposal Pop Up Not Found", False)
        return False
    else:
        element.click()
        return True

def checkProposalSent(driver):
    try: 
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[30]')))
        # I need to compare the the class of the toast to see if it is a proposal sent or not if class="w-toast--success" then proposalSent = True
        # Extract the element with XPath
        toast_element = driver.find_element(By.XPATH, '/html/body/div[30]')
        # Get the class attribute
        class_attribute = toast_element.get_attribute("class")
        
        if class_attribute == "w-Toast_success":
            notify("COMPLETED: BUFF 163 BOT", "Proposal sent to the seller", True)
        else:
            notify("FAILED: BUFF 163 BOT", "Proposal not sent to the seller", True)
        update_bought_item_gsheet(driver.current_url)
    except TimeoutException:
        notify("FAILED: BUFF 163 BOT", "Proposal Status Not Found", False)

def purchase(driver, request, listing, maximumFloat, maximumPrice, divTitle):
    initPurchase(driver, request)
    
    listingStatus = checkListing(driver, listing, maximumFloat, maximumPrice, divTitle)
    
    if listingStatus == True:

        beginPurchaseClicked = clickToBeginPurchase(driver, listing, divTitle)
        
        if beginPurchaseClicked == True:
            PurchaseClicked = clickToPurchase(driver)
            if PurchaseClicked == True:
                ProposalClicked = clickToSendProposal(driver)
                if ProposalClicked == True:
                    checkProposalSent(driver)
    else:
        notify("FAILED: BUFF 163 BOT", "Listing Not Found", False)
    driver.quit()