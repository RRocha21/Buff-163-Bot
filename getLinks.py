import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# Define the scope and credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('buff-bot-e6cdb8b80af6.json', scope)

# Authorize the client
client = gspread.authorize(credentials)

# Open the Google Sheet
sheet = client.open('Buff163-Skins').sheet1

# Get the data from columns B, C, D
data = sheet.get_all_values()[1:]  # Skipping the header row

# Initialize a dictionary to store the data
output = {}

# Iterate through the data and format it
# Iterate through the data and format it

scraper_number = 1
scraper_size = 18

for row in data:
    scraper_name, link, float_value, price = row[1], row[2], row[3].replace(',', '.'), row[4].replace(',', '.')

    link = row[1]  # Remove the query string from the link
    if link == '':  
        break
        
    float_value = float(row[2].replace(',', '.'))  # Remove the comma from the float value
    price = float(row[3].replace(',', '.'))  # Remove the comma from the price
    
    if 'scraper{}'.format(scraper_number) not in output:
        output['scraper{}'.format(scraper_number)] = [{'link': link, 'float': float_value, 'price': price}]
    else:
        if len(output['scraper{}'.format(scraper_number)]) < scraper_size:
            output['scraper{}'.format(scraper_number)].append({'link': link, 'float': float_value, 'price': price})
        else:
            scraper_number += 1
            output['scraper{}'.format(scraper_number)] = [{'link': link, 'float': float_value, 'price': price}]

# Format the output as specified
file_path = 'buff2.json'

with open(file_path, 'w') as f:
    json.dump(output, f, indent=4)
    
print('Done')