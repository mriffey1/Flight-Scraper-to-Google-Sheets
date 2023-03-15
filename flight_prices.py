import gspread
import time
import datetime
from datetime import datetime as dt, timedelta
from gspread_formatting import *
from gspread_formatting.dataframe import format_with_dataframe, BasicFormatter
from gspread_formatting import Color
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
from gspread_dataframe import set_with_dataframe
import numpy as np
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utils import gspread_creds as use_me
from utils import format_sheet

def scrolling():
    height = driver.execute_script('return document.body.scrollHeight')
    scroll_height = 0
    total_height = int(driver.execute_script("return document.documentElement.scrollHeight"))
    print(total_height)
    scroll_height = int(scroll_height + (total_height / 2))
    print("Scroll Height:")
    print(scroll_height)
    for i in range(1, scroll_height, 5):
        driver.execute_script("window.scrollTo(0, {});".format(i))
        time.sleep(.008)

def refresh_page():
     driver.refresh()
     time.sleep(10)
     scrolling()
    
s = Service("C:\Windows\chromedriver.exe")
caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "none" 
options = webdriver.ChromeOptions() 
options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
options.add_argument("disable-gpu")  ##renderer timeout
# options.add_argument("--headless=new")
options.add_argument('--blink-settings=imagesEnabled=false')
options.add_argument("--start-maximized")
# options.add_argument("--window-size=1920,1080")
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features")
options.add_argument('--disable-blink-features=AutomationControlled')

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

for i in range(3):
    startdate = sdate + datetime.timedelta(days=i+1)
    enddate = sdate - datetime.timedelta(days=i) # date - days
    modified = enddate.strftime("%Y%m%d")
    
    url = "https://www.priceline.com/m/fly/search/IND-NRT-" + modified + "/?cabin-class=ECO&no-date-search=false&num-adults=2&num-youths=2&sbsroute=slice1&search-type=00"
    urls.append(url)
    # modified = startdate.strftime("%Y%m%d")
    # url = "https://www.priceline.com/m/fly/search/IND-NRT-" + modified + "/?cabin-class=ECO&no-date-search=false&num-adults=2&num-youths=2&sbsroute=slice1&search-type=00"
    

for url in urls:
    time.sleep(2)
    driver.get(url)
    time.sleep(10)
    driver.get_screenshot_as_file("screenshot9.png")
    scrolling()
 
    exception_count = 3
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
        # try:
        driver.implicitly_wait(5)
        containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'sc-gsDKAQ sc-dkPtRN iyMkCh ebwuWR')]")
            

    for item in containers[:5]:
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

        # The for loop below goes through and grabs both sets of layover airport info since both items have the same div id.
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
                    # layover_name = (layover_name + "/" + code.text) 
                    layover_name = '-'.join(code.text for code in layover_airports_search if code.text)
                    # layover_name = "".join([layover_name, "/",  code.text])
                except ValueError:
                    pass

        arrival_time_search = item.find_element(By.XPATH, ".//div[contains(@data-testid, 'arrival-time')]")
        flight_price_Search = item.find_element(By.XPATH, ".//div[contains(@data-testid, 'display-price')]")
        duration_search = item.find_element(By.XPATH, ".//div[contains(@data-testid, 'slice-duration')]")
        # This item adds the data to a list
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
        


# credentials = ServiceAccountCredentials.from_json_keyfile_name("driveapi.json", scopes)
# file = gspread.authorize(credentials)
# sheet = file.open("FlightPricing")
# sheet = sheet.sheet1

sheet, file = use_me()

dataframe = pd.DataFrame(sheet.get_all_records())

# The df_airline sets the data fields to be inserted into google sheets. The set dataframe actually uploads the data
df_airline = pd.DataFrame(airline_info,
                          columns=['Departure Date', 'Airline Name', 'Departure Airport', 'Departure Time', '# Layover Stops',
                                   'Total Layover Duration', 'Layover Airports', 'Arrival Airport', 'Arrival Time',
                                   'Arrival Date', 'Total Duration of Travel', 'Price', 'Date Added'])


frames = [dataframe, df_airline]
result = pd.concat(frames)
result.reset_index(drop=True, inplace=True)
sheet.clear()

set_with_dataframe(sheet, result)

format_to = len(result.index)
set_row_height(sheet, '1:' + str(format_to + 1), 40)

format_sheet()
driver.quit()