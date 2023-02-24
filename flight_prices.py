from urllib.request import urlopen
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import requests
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import time 
# import pandas as pd

# driver = Service(r"C:\Windows\chromedriver.exe")
# op = webdriver.ChromeOptions()
# s = webdriver.Chrome(service=driver, options=op)


s = Service("C:\Windows\chromedriver.exe")
driver = webdriver.Chrome(service=s)


driver.get("https://www.priceline.com/m/fly/search/IND-NRT-20230603/NRT-IND-20230617/?cabin-class=ECO&no-date-search=false&num-adults=2&num-children=2&sbsroute=slice1&search-type=0000&vrid=c833c34867c4370bcc4061cd72419759")
driver.implicitly_wait(10)

# URL = "https://www.priceline.com/m/fly/search/IND-NRT-20230603/NRT-IND-20230617/?cabin-class=ECO&no-date-search=false&num-adults=2&num-children=2&sbsroute=slice1&search-type=0000&vrid=c833c34867c4370bcc4061cd72419759"

# r = requests.get(URL,headers={"User-Agent":"Mozilla/5.0"})
# soup = BeautifulSoup(r.text,"html.parser")

airline_name = []

airline_name_search = str(driver.find_element(By.XPATH, "//div[contains(@class, 'SliceDisplay__AirlineText')]").text)
airline_name.append(airline_name_search)

time.sleep(3)

# soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib
# print(soup.prettify())

two_dimensions = [airline_name]

scopes = [
'https://www.googleapis.com/auth/spreadsheets',
'https://www.googleapis.com/auth/drive'
]

credentials = ServiceAccountCredentials.from_json_keyfile_name("driveapi.json", scopes) #access the json key you downloaded earlier 
file = gspread.authorize(credentials) # authenticate the JSON key with gspread
sheet = file.open("FlightPricing") #open sheet
sheet = sheet.sheet1 #replace sheet_name with the name that corresponds to yours, e.g, it can be sheet1

# This is a test list. Would need to replace with data from web scraper

# my_list = [['Not Ford', 'Not Lancia', 'White'], ['c', 'd', 'b'], ['e', 'f', 'd'], ['g', 'h', 'e']]

# my_list = [['Not Ford']]

# # This adds new rows using a list. 
# sheet.append_rows(my_list)

sheet.append_rows(two_dimensions)

# all_cells = sheet.range('A1:C8')
# for cell in all_cells:
#  print(cell.value)


