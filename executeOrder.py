import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import pickle
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from win11toast import toast

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

def purchase(driver, listing):
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[7]/div/div[7]/table/tbody/tr[{}]/td[6]/a'.format(listing+2))))
    # driver.find_element(By.XPATH, '/html/body/div[7]/div/div[7]/table/tbody/tr[{}]/td[6]/a'.format(listing+2)).click() #used to purchase
    element = driver.find_element(By.XPATH, '/html/body/div[7]/div/div[7]/table/tbody/tr[{}]/td[6]/a'.format(listing+2))
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    element.click()
    purchaseCompleted = False
    proposalSent = False
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[27]/div[2]/div[4]/a')))
        driver.find_element(By.XPATH, '/html/body/div[27]/div[2]/div[4]/a').click()
        print('success')
        purchaseCompleted = True
    except TimeoutException:
        print("Loading took too much time!")
    
    if purchaseCompleted == False:
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[24]/div[2]/div[4]/a')))
            driver.find_element(By.XPATH, '/html/body/div[28]/div[2]/div[4]/a').click()
            print('success')
            purchaseCompleted = True
        except TimeoutException:
            print("Loading took too much time!")
            
    if purchaseCompleted == False:
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[26]/div[2]/div[4]/a')))
            driver.find_element(By.XPATH, '/html/body/div[26]/div[2]/div[4]/a').click()
            print('success')
            purchaseCompleted = True
        except TimeoutException:
            print("Loading took too much time!")
            
    if purchaseCompleted == False:
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[25]/div[2]/div[4]/a')))
            driver.find_element(By.XPATH, '/html/body/div[25]/div[2]/div[4]/a').click()
            print('success')
            purchaseCompleted = True
        except TimeoutException:
            print("Loading took too much time!")

    if purchaseCompleted == True:
        try: 
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[29]/div[2]/div/div[2]/a')))
            driver.find_element(By.XPATH, '/html/body/div[29]/div[2]/div/div[2]/a').click()
            print('Clicked to Send Prososal to Seller')
            proposalSent = True
        except TimeoutException:
            print("Loading took too much time for the proposal!")
        
        if proposalSent == False:
            try: 
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[28]/div[2]/div/div[2]/a')))
                driver.find_element(By.XPATH, '/html/body/div[28]/div[2]/div/div[2]/a').click()
                print('Clicked to Send Prososal to Seller')
                proposalSent = True
            except TimeoutException:
                print("Loading took too much time for the proposal!")
                
        if proposalSent == False:
            try: 
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[30]/div[2]/div/div[2]/a')))
                driver.find_element(By.XPATH, '/html/body/div[30]/div[2]/div/div[2]/a').click()
                print('Clicked to Send Prososal to Seller')
                proposalSent = True
            except TimeoutException:
                print("Loading took too much time for the proposal!")
                
        if proposalSent == False:
            try: 
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[27]/div[2]/div/div[2]/a')))
                driver.find_element(By.XPATH, '/html/body/div[27]/div[2]/div/div[2]/a').click()
                print('Clicked to Send Prososal to Seller')
                proposalSent = True
            except TimeoutException:
                print("Loading took too much time for the proposal!")
    if proposalSent == True:
        try: 
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[30]')))
            # I need to compare the the class of the toast to see if it is a proposal sent or not if class="w-toast--success" then proposalSent = True
            # Extract the element with XPath
            toast_element = driver.find_element(By.XPATH, '/html/body/div[30]')
            # Get the class attribute
            class_attribute = toast_element.get_attribute("class")
            
            if class_attribute == "w-Toast_success":
                print("Proposal sent to Seller")
                proposalSent = True
            else:
                print("Proposal was not sent to Seller")
            proposalSent = False  
        except TimeoutException:
            print("Proposal was not sent to Seller")
            proposalSent = False

    if proposalSent == True:
        notify("COMPLETED: BUFF 163 BOT", "An item has been purchased and a proposal has been sent to the seller", True)
    else:
        if purchaseCompleted == True:
            notify("FAILED: BUFF 163 BOT", "An item has been purchased but a proposal could not be sent to the seller", False)
        else:
            notify("FAILED: BUFF 163 BOT", "An item could not be purchased", False)

    time.sleep(5)