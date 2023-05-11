import time
import datetime
from gspread_formatting import *
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
from gspread_dataframe import set_with_dataframe
import numpy as np
from selenium.common.exceptions import TimeoutException
from utils import gspread_creds as use_me
from utils import format_sheet, chrome_options, program_log
import email_test

def test_function(name_string):
    if name_search == "Multiple":
        name_search2 = item.find_element(By.XPATH, ".//div[contains(@data-testid, 'multiple-airlines-icon-with-tooltip')]")
        actions = ActionChains(driver)
        actions.move_to_element(name_search2).perform()
        time.sleep(5)
        multiple_airline = item.find_element(By.XPATH, ".//div[contains(@class, 'MultipleAirlinesIconWithTooltip__StyledMultipleAirlineTooltip')]")
        return multiple_airline.text
    else:
        return name_search
 
# Function to refresh page
def refresh_page():
     driver.refresh()
     time.sleep(10)
     
# Starting chrome service and options    
s = Service("/lib/chromium-browser/libs/chromedriver")
options = chrome_options()

driver = webdriver.Chrome(options=options, service=s)
sdate = datetime.date.today() + datetime.timedelta(days=324+1)

urls = []
airline_info = []
airline_dict = {}
total_time = 0
layover_name = ""
first_layover_name = ""
second_layover_name = ""
iterations = 0
current_date = datetime.date.today()
date_added = current_date.strftime("%m/%d/%Y")

departure_code = []
departure_code.append("IND")
departure_code.append("CHI")

print(f"-------------------- {date_added} --------------------")
program_log("Application", "started")
# Getting dates before and after sdate (start date)
for i in range(2):
    startdate = sdate + datetime.timedelta(days=i+1)
    enddate = sdate - datetime.timedelta(days=i)  # date - days
    
    modified_start = startdate.strftime("%Y%m%d")
    modified_end = enddate.strftime("%Y%m%d")

    url_template = "https://www.priceline.com/m/fly/search/{depart_code}-NRT-{date}/?cabin-class=ECO&no-date-search=false&num-adults=2&num-youths=2&sbsroute=slice1&search-type=10"

    for depart_code in departure_code:
        url_end = url_template.format(depart_code=depart_code, date=modified_end)
        url_start = url_template.format(depart_code=depart_code, date=modified_start)
    
        urls.extend([url_end, url_start])

      

exception_count = 3    

for url in urls:   
    driver.get(url)
    time.sleep(3)
    
    flight_departure_date = driver.execute_script('return pclntms["dataDictionary"]["travelStartDate"]')
   
    while True:
        try:
            WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//li[contains(@class, 'wrapComponentsRenderInView__InViewWrapper-sc-1a56ibf-0 bSIksk')]")))
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
        driver.implicitly_wait(1)
        containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'sc-gsDKAQ sc-dkPtRN YHaLn iwXGLS')]")
    if len(containers) == 0:
        email_message = "No items have been found."
        email_test.send_email("Error: No Items Found", email_message)
    else:     
        for item in containers[:10]:
            driver.execute_script("arguments[0].scrollIntoView();", item)
            flight_leave_date = driver.find_element(By.XPATH, "//input[contains(@data-selenium, 'flight-calendar')]").get_attribute('value')
            name_search = item.find_element(By.XPATH, ".//div[contains(@class, 'SliceDisplay__AirlineText')]").text
            
            final_airline_names = test_function(name_search)
                
            departure_time_search = item.find_element(By.XPATH, ".//div[contains(@data-testid, 'departure-time')]")
            number_of_stops_search = item.find_element(By.XPATH, ".//div[contains(@data-testid, 'slice-details-title')]")
            arrival_date_search = item.find_element(By.XPATH, ".//span[contains(@class, 'SliceTitle__SummaryText')]")
           
            arrival_airport_search = item.find_element(By.XPATH, ".//span[contains(@data-testid, 'arrival-airport')]")
            departure_airport_search = item.find_element(By.XPATH, ".//span[contains(@data-testid, 'departure-airport')]")
            layout_airport_search = item.find_elements(By.XPATH, ".//div[contains(@data-testid, 'layover-airport')]")
            layover_airports_search = item.find_elements(By.XPATH, ".//div[contains(@data-testid, 'layover-duration')]")
            converting_arrival_date = arrival_date_search.text.replace("Arrives:", "").replace(",", "").strip().split(" ")
            conversions = {
                "Jan": "1", 
                "Feb": "2", 
                "Mar": "3", 
                "Apr": "4",
                "May": "5", 
                "Jun": "6", 
                "Jul": "7", 
                "Aug": "8",
                "Sep": "9", 
                "Oct": "10", 
                "Nov": "11", 
                "Dec": "12"
                }
            
            converted_arrival_date = (conversions[converting_arrival_date[1]]+ "/" + converting_arrival_date[2] + "/" + "2024")
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
                flight_departure_date,
                final_airline_names,
                departure_airport_search.text,
                departure_time_search.text,
                number_of_stops_search.text,
                hours_minutes,
                layover_name,
                arrival_airport_search.text,
                arrival_time_search.text,
                converted_arrival_date,
                duration_search.text,
                flight_price_Search.text,
                date_added])
        
sheet, file = use_me()

dataframe = pd.DataFrame(sheet.get_all_records())
program_log("All current data from spreadsheet", "obtained")

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
program_log("Current and new data", "concatenated together")
sheet.clear()
program_log("Existing sheet", "cleared")
set_with_dataframe(sheet, result)
program_log("Existing sheet", "updated with new data")
format_to = len(df_airline.index)
set_row_height(sheet, '1:' + str(format_to + 1), 40)

format_sheet()
program_log("Program", "successfully ran")
completion_msg = "Program has ran successfully."
email_test.send_email("Successfully ran flight tracker.", completion_msg)
print("-------------------- END OF LINE --------------------\n\n")
driver.quit()