from selenium import webdriver
import time

# List of URLs
urls = [
    "https://buff.163.com/goods/781577",
    "https://buff.163.com/goods/781568",
    "https://buff.163.com/goods/781592",
    "https://buff.163.com/goods/781567",
    "https://buff.163.com/goods/781614",
    "https://buff.163.com/goods/781582",
    "https://buff.163.com/goods/781632"
]

# Initialize Chrome WebDriver
driver = webdriver.Chrome()

# Open tabs with different URLs
for url in urls:
    driver.execute_script("window.open('{}', '_blank');".format(url))

# Switch to the first tab (optional)
driver.switch_to.window(driver.window_handles[0])

# Loop through each tab and refresh
for i, handle in enumerate(driver.window_handles):
    driver.switch_to.window(handle)
    driver.refresh()
    time.sleep(5)

# Close the browser
driver.quit()