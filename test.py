from urllib.request import urlopen
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
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
import time 
import requests
from bs4 import BeautifulSoup
import csv
import urllib
import urllib.request
from urllib.request import Request, urlopen
# import pandas as pd
from lxml import etree

s = Service("C:\Windows\chromedriver.exe")
driver = webdriver.Chrome(service=s)
driver.maximize_window()

driver.get("https://www.priceline.com/m/fly/search/IND-NRT-20230603/NRT-IND-20230617/?cabin-class=ECO&no-date-search=false&num-adults=2&num-children=2&sbsroute=slice1&search-type=0000&vrid=c833c34867c4370bcc4061cd72419759")
# driver.implicitly_wait(100)
airline_info = []
wait = WebDriverWait(driver,30)
for i in range(5):

    wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'RetailItinerarystyles__CursorStyles')]")))

    containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'RetailItinerarystyles__CursorStyles')]")

    for item in containers:
        name_search = item.find_element(By.XPATH, ".//div[contains(@class, 'SliceDisplay__AirlineText')]")
        departure_time_search = item.find_element(By.XPATH, ".//div[contains(@data-testid, 'departure-time')]")
        number_of_stops_search = item.find_element(By.XPATH, ".//div[contains(@data-testid, 'slice-details-title')]")
        arrival_date_search = item.find_element(By.XPATH, ".//span[contains(@class, 'SliceTitle__SummaryText')]")
        arrival_airport_search = item.find_element(By.XPATH, ".//span[contains(@data-testid, 'arrival-airport')]")
        departure_airport_search = item.find_element(By.XPATH, ".//span[contains(@data-testid, 'departure-airport')]")
        layout_airport_search = item.find_element(By.XPATH, ".//div[contains(@data-testid, 'layover-airport')]")
        arrival_time_search = item.find_element(By.XPATH, ".//div[contains(@data-testid, 'arrival-time')]")
        flight_price_Search = item.find_element(By.XPATH, ".//div[contains(@data-testid, 'display-price')]")
        duration_search = item.find_element(By.XPATH, ".//div[contains(@data-testid, 'slice-duration')]")

        airline_info.append([name_search.text, departure_time_search.text, number_of_stops_search.text, arrival_date_search.text,  arrival_airport_search.text, departure_airport_search.text, layout_airport_search.text,  arrival_time_search.text, flight_price_Search.text,  duration_search.text])
        driver.execute_script("arguments[0].scrollIntoView(true);",containers[len(containers)-1])
        
print(airline_info)