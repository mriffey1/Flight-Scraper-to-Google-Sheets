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
from selenium.webdriver import ActionChains


s = Service("C:\Windows\chromedriver.exe")
caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "none"  #  complete

# driver.get("http://google.com")

options = webdriver.ChromeOptions()  # Initializing Chrome Options from the Webdriver
options.add_experimental_option("useAutomationExtension", False)  # Adding Argument to Not Use Automation Extension
options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Excluding enable-automation Switch
options.add_argument("disable-popup-blocking")
options.add_argument("disable-notifications")
options.add_argument("disable-gpu")  ##renderer timeout
options.add_argument('--disable-blink-features=AutomationControlled')
# options.add_argument('--headless')

# driver = webdriver.Chrome(desired_capabilities=caps, service=s, options=options)
driver = webdriver.Chrome(options=options, service=s)

sdate = datetime.datetime(2023, 6, 3)




height = driver.execute_script('return document.body.scrollHeight')

scroll_height = 0

urls = []
airline_info = []
total_time = 0
layover_name = ""
first_layover_name = ""
second_layover_name = ""
current_date = datetime.date.today()
date_added = current_date.strftime("%m/%d/%Y")
for i in range(3):
    startdate = sdate + datetime.timedelta(days=i)
    enddate = sdate - datetime.timedelta(days=i) # date - days
    modified = enddate.strftime("%Y%m%d")
    url = "https://www.priceline.com/m/fly/search/IND-NRT-" + modified + "/?cabin-class=ECO&no-date-search=false&num-adults=2&num-youths=2&sbsroute=slice1&search-type=00&vrid=4bbd06407109ddc54a9b547324155937"
    urls.append(url)
   
for url in urls:
    driver.get(url)
    driver.maximize_window()
    
    driver.implicitly_wait(15)
    # driver.execute_script("window.scrollTo(0, Y)")
    # wait = WebDriverWait(driver, 40)
    height = driver.execute_script('return document.body.scrollHeight')
    scroll_height = 0
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, "
    #                                                       "'RetailItineraryNewstyles__CursorStyles')]")))
    flight_leave_date = driver.find_element(By.XPATH, "//input[contains(@data-selenium, 'flight-calendar')]").get_attribute('value')
    for i in range(5):
        scroll_height = scroll_height + (height / 10)
        driver.execute_script('window.scrollTo(0,arguments[0]);', scroll_height)
        time.sleep(2)

    # This is establishing the overall div for each element group
        containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'RetailItineraryNewstyles__CursorStyles')]")

    for item in containers:
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
        
      

        # This item adds the data to a list
        # airline_info.append([
        #     name_search.text,
        #     departure_time_search.text])

scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name("driveapi.json", scopes)
file = gspread.authorize(credentials)
sheet = file.open("FlightPricing")
sheet = sheet.sheet1

dataframe = pd.DataFrame(sheet.get_all_records())
# # The df_airline sets the data fields to be inserted into google sheets. The set dataframe actually uploads the data
df_airline = pd.DataFrame(airline_info,
                          columns=['Depature Date', 'Airline Name', 'Departure Airport', 'Departure Time', '# Layover Stops',
                                   'Total Layover Duration', 'Layover Airports', 'Arrival Airport', 'Arrival Time',
                                   'Arrival Date', 'Total Duration of Travel', 'Price', 'Date Added'])

frames = [dataframe, df_airline]
result = pd.concat(frames)

sheet.clear()

set_with_dataframe(sheet, result)

header_row = cellFormat(
    backgroundColor=color(1, .6, .8),
    textFormat=textFormat(bold=True, foregroundColor=color(0, 0, 0)),
    horizontalAlignment='CENTER'
)
format_cell_range(sheet, 'A1:M1', header_row)

rule = ConditionalFormatRule(
    ranges=[GridRange.from_a1_range('L2:L', sheet)],
    booleanRule=BooleanRule(
        condition=BooleanCondition('NUMBER_LESS', ['1700']),
        format=CellFormat(textFormat=textFormat(bold=True), backgroundColor=Color(.8, 1, 0.8))
    )
)

# rules = ConditionalFormatRule(
#     ranges=[GridRange.from_a1_range('K2:K', sheet)],
#     booleanRule=BooleanRule(
#         condition=BooleanCondition('NUMBER_LESS', ['1700']),
#         format=CellFormat(textFormat=textFormat(bold=True), backgroundColor=Color(.8, 1, 0.8))
#     )
# )

fmt = cellFormat(
    backgroundColor=color(1, 1, 1),
    textFormat=textFormat(bold=False, foregroundColor=color(0, 0, 0)),
    horizontalAlignment='CENTER',
    borders=borders(bottom=border('SOLID')),
    padding=padding(left=3),

)
format_cell_range(sheet, 'A2:M', fmt)
format_to = len(result.index)

set_row_height(sheet, '1:' + str(format_to + 1), 40)


rules = get_conditional_format_rules(sheet)
rules.clear()
rules.append(rule)
rules.save()
  
driver.quit()