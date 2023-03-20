import time
import datetime
from gspread_formatting import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
from gspread_dataframe import set_with_dataframe
import numpy as np
from selenium.common.exceptions import TimeoutException
from utils import gspread_creds as use_me
from utils import format_sheet, chrome_options

def scrolling():
    scroll_height = 0
    total_height = int(driver.execute_script("return document.documentElement.scrollHeight"))
    print(total_height)
    scroll_height = int(scroll_height + total_height)
    print("Scroll Height:")
    print(scroll_height)
    for i in range(1, scroll_height, 10):
        driver.execute_script("window.scrollTo(0, {});".format(i))
        time.sleep(.001)

def refresh_page():
     driver.refresh()
     time.sleep(10)
     scrolling()
    
s = Service("C:\Windows\chromedriver.exe")
options = chrome_options()

driver = webdriver.Chrome(options=options, service=s)
sdate = datetime.datetime(2023, 6, 3)

urls = []
airline_info = []
total_time = 0
layover_name = ""
first_layover_name = ""
second_layover_name = ""
iterations = 0
current_date = datetime.date.today()
date_added = current_date.strftime("%m/%d/%Y")

departure_code = []
departure_code.append("IND")
departure_code.append("LAX")
departure_code.append("CHI")

for i in range(3):
    startdate = sdate + datetime.timedelta(days=i+1)
    enddate = sdate - datetime.timedelta(days=i) # date - days
    
    for depart_code in departure_code:
        modified = enddate.strftime("%Y%m%d")
        url = "https://www.priceline.com/m/fly/search/"+ depart_code + "-NRT-" + modified + "/?cabin-class=ECO&no-date-search=false&num-adults=2&num-youths=2&sbsroute=slice1&search-type=00"
        urls.append(url)
        modified = startdate.strftime("%Y%m%d")
        url = "https://www.priceline.com/m/fly/search/"+ depart_code + "-NRT-" + modified + "/?cabin-class=ECO&no-date-search=false&num-adults=2&num-youths=2&sbsroute=slice1&search-type=00"
        urls.append(url)
        
print(urls)

exception_count = 3    

for url in urls:
    time.sleep(2)
    driver.get(url)
    time.sleep(10)
    scrolling()
  
    
    time.sleep(2)
    while True:
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//li[contains(@class, 'wrapComponentsRenderInView__InViewWrapper-sc-1a56ibf-0 bSIksk')]")))
            break
        except TimeoutException as e: 
            if exception_count > 0:
                print("Printing exception count: ")
                exception_count -= 1
                print(exception_count)
                refresh_page()
            else:
                print("Failed to function after 3 times")
                print(e)
   
    for i in range(5):
        driver.implicitly_wait(5)
        containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'sc-gsDKAQ sc-dkPtRN iyMkCh ebwuWR')]")
            
    for item in containers[:10]:
        flight_leave_date = driver.find_element(By.XPATH, "//input[contains(@data-selenium, 'flight-calendar')]").get_attribute('value')
        name_search = item.find_element(By.XPATH, ".//div[contains(@class, 'SliceDisplay__AirlineText')]")
        departure_time_search = item.find_element(By.XPATH, ".//div[contains(@data-testid, 'departure-time')]")
        number_of_stops_search = item.find_element(By.XPATH, ".//div[contains(@data-testid, 'slice-details-title')]")
        arrival_date_search = item.find_element(By.XPATH, ".//span[contains(@class, 'SliceTitle__SummaryText')]")
        split_text = arrival_date_search.text.replace("Arrives: ", "")
        arrival_airport_search = item.find_element(By.XPATH, ".//span[contains(@data-testid, 'arrival-airport')]")
        departure_airport_search = item.find_element(By.XPATH, ".//span[contains(@data-testid, 'departure-airport')]")
        layout_airport_search = item.find_elements(By.XPATH, ".//div[contains(@data-testid, 'layover-airport')]")
        layover_airports_search = item.find_elements(By.XPATH, ".//div[contains(@data-testid, 'layover-duration')]")

        for lay in layout_airport_search:
            if lay:
                new_name = lay.text.replace("h", ",").replace(" ", "").replace("m", "").strip()
                try:
                    a, b = map(int, str(new_name).split(',', maxsplit=1))
                    hours_amount = a * 60
                    minutes_amount = b
                    total_time = hours_amount + minutes_amount
                    array_time = np.array(total_time)
                    hours_minutes = '{:2d}h {:02d}m'.format(*divmod(total_time, 60))
                except ValueError:
                    pass

        for code in layover_airports_search:
            if code:
                try:
                    layover_name = '-'.join(code.text for code in layover_airports_search if code.text)
                except ValueError:
                    pass

        arrival_time_search = item.find_element(By.XPATH, ".//div[contains(@data-testid, 'arrival-time')]")
        flight_price_Search = item.find_element(By.XPATH, ".//div[contains(@data-testid, 'display-price')]")
        duration_search = item.find_element(By.XPATH, ".//div[contains(@data-testid, 'slice-duration')]")
        
        airline_info.append([
            flight_leave_date,
            name_search.text,
            departure_airport_search.text,
            departure_time_search.text,
            number_of_stops_search.text,
            hours_minutes,
            layover_name,
            arrival_airport_search.text,
            arrival_time_search.text,
            split_text,
            duration_search.text,
            flight_price_Search.text,
            date_added])
        
sheet, file = use_me()

dataframe = pd.DataFrame(sheet.get_all_records())

df_airline = pd.DataFrame(airline_info,
                          columns=['Departure Date', 
                                   'Airline Name', 
                                   'Departure Airport', 
                                   'Departure Time', 
                                   '# Layover Stops', 
                                   'Total Layover Duration', 
                                   'Layover Airports', 
                                   'Arrival Airport', 
                                   'Arrival Time', 
                                   'Arrival Date', 
                                   'Total Duration of Travel', 
                                   'Price', 
                                   'Date Added'])

frames = [dataframe, df_airline]
result = pd.concat(frames)
result.reset_index(drop=True, inplace=True)

sheet.clear()

set_with_dataframe(sheet, result)

format_to = len(result.index)
set_row_height(sheet, '1:' + str(format_to + 1), 40)

format_sheet()
driver.quit()