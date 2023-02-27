import gspread
import time
import datetime
from gspread_formatting import *
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
from gspread_dataframe import set_with_dataframe

# Identifying chrome driver and maximizing the screen when ran
s = Service("C:\Windows\chromedriver.exe")
driver = webdriver.Chrome(service=s)
driver.maximize_window()

# Driver is opening the website
driver.get("https://www.priceline.com/m/fly/search/IND-NRT-20230603/NRT-IND-20230617/?cabin-class=ECO&no-date-search=false&num-adults=2&num-children=2&sbsroute=slice1&search-type=0000&vrid=c833c34867c4370bcc4061cd72419759")

# This is waiting for contents to load on the page, along with setting variables for scrolling on page
wait = WebDriverWait(driver,30)
wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'RetailItinerarystyles__CursorStyles')]")))
time.sleep(2)
height = driver.execute_script('return document.body.scrollHeight')

scroll_height = 0

airline_info = []
current_date = datetime.date.today()
date_added = current_date.strftime("%B %d %Y")

# This is iterating through the elements found on the page
for i in range(5):

    scroll_height = scroll_height + (height/10)
    driver.execute_script('window.scrollTo(0,arguments[0]);',scroll_height)
    time.sleep(2)

# This is establishing the overall div for each element group
containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'RetailItinerarystyles__CursorStyles')]")

total_time = 0
layover_name = ""

# This is iterating through each element and pulling out the individual details. 
# Completing it this way ensures the child elements belong to the parent element and we have a set of matching data.
for item in containers:
    name_search = item.find_element(By.XPATH, ".//div[contains(@class, 'SliceDisplay__AirlineText')]")
    departure_time_search = item.find_element(By.XPATH, ".//div[contains(@data-testid, 'departure-time')]")
    number_of_stops_search = item.find_element(By.XPATH, ".//div[contains(@data-testid, 'slice-details-title')]")
    arrival_date_search = item.find_element(By.XPATH, ".//span[contains(@class, 'SliceTitle__SummaryText')]")
    arrival_airport_search = item.find_element(By.XPATH, ".//span[contains(@data-testid, 'arrival-airport')]")
    departure_airport_search = item.find_element(By.XPATH, ".//span[contains(@data-testid, 'departure-airport')]")
    layout_airport_search = item.find_elements(By.XPATH, ".//div[contains(@data-testid, 'layover-airport')]")
    layover_airports_search = item.find_elements(By.XPATH, ".//div[contains(@data-testid, 'layover-duration')]")

# The for loop below goes through and grabs both sets of layover airport info since both items have the same
# div id. 
    for lay in layout_airport_search:
        if lay:
            new_name = lay.text.replace("h", ",").replace(" ", "").replace("m", "").strip()
            try:
                a,b = map(int,str(new_name).split(',',maxsplit=1))
                hours_amount = a * 60
                minutes_amount = b
                total_time = hours_amount + minutes_amount
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
        name_search.text, 
        departure_airport_search.text, 
        departure_time_search.text, 
        number_of_stops_search.text, 
        total_time,
        layover_name,
        arrival_airport_search.text, 
        arrival_time_search.text, 
        arrival_date_search.text,  
        duration_search.text, 
        flight_price_Search.text, 
        date_added])
   
scopes = ['https://www.googleapis.com/auth/spreadsheets',
'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name("driveapi.json", scopes) 
file = gspread.authorize(credentials)
sheet = file.open("FlightPricing")
sheet = sheet.sheet1 

df_airline = pd.DataFrame(airline_info, columns = ['Airline Name', 'Departure Airport', 'Departure Time', '# Layover Stops', 'Total Layover Duration', 'Layover Airports','Arrival Airport', 'Arrival Time', 'Arrival Date', 'Total Duration of Travel', 'Price', 'Date Added'])
set_with_dataframe(sheet, df_airline)


driver.quit()