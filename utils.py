#type: ignore
import gspread
from gspread_formatting import *
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import datetime

# Google Sheets API credential
def gspread_creds():
    scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name("/home/megan/Python/Flight-Scraper-Selenium/driveapi.json", scopes)
    file = gspread.authorize(credentials)
    sheet = file.open("FlightPricing").sheet1
    
    return sheet, file

# Chrome options
def chrome_options():
    options = webdriver.ChromeOptions() 
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    options.add_argument("disable-gpu")  ##renderer timeout
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument("--start-maximized")
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features")
    options.add_argument('--disable-blink-features=AutomationControlled')
    return options

sheet, file = gspread_creds()

def program_log(logging_item, what_done):
    now = datetime.datetime.today()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    return print(logging_item + " has/have been " + what_done + " at " + dt_string)

# Google API for formatting sheet
def format_sheet():
    spreadsheetId = "sheet_id"  
    sh = file.open_by_key(spreadsheetId)
    rules = get_conditional_format_rules(sheet)
    rules.clear()
    rules.save()
    program_log("Conditional Rules", "cleared")
    formula = '=IF($L1:$L1<>"", $L:$L<=600, "Empty")'
    body = {
      "requests": [
          {
              "addConditionalFormatRule": {
                  "index": 0,
                  "rule": {
                      "ranges": [{"sheetId": sheet.id}],
                      "booleanRule": {
                          "condition": {
                              "type": "CUSTOM_FORMULA",
                              "values": [{"userEnteredValue": formula}],
                          },
                          "format": {
                              "backgroundColor": {
                                  "red": 0.7882,
                                  "green": 0.9725,
                                  "blue": 1,
                                  "alpha": 1
                              },
                              "textFormat": {
                              "bold": True
                          }
                          }
                          
                      }
                  }
              }
              
          },
          {
              'clearBasicFilter' : {
                  'sheetId': sheet.id
              }
          },
          {
              "setBasicFilter": {
                  "filter": {
                      "range": {    
                          "sheetId": sheet.id,
                          "startColumnIndex": 0,
                          "endColumnIndex": 13
                      },            
                  }
              }
          }   
      ]
    }

    header_row = cellFormat(
        backgroundColor=color(1, .6, .8),
        textFormat=textFormat(bold=True, foregroundColor=color(0, 0, 0)),
        horizontalAlignment='CENTER'
    )
  
    format_row = cellFormat( 
        backgroundColor=color(1, .6, .8),
        textFormat=textFormat(bold=True, foregroundColor=color(0, 0, 0)),
        horizontalAlignment='CENTER',
        verticalAlignment='MIDDLE'
    )

    fmt = cellFormat(
        backgroundColor=color(1, 1, 1),
        textFormat=textFormat(bold=False, foregroundColor=color(0, 0, 0)),
        horizontalAlignment='CENTER',
        borders=borders(bottom=border('SOLID')),
        padding=padding(left=3),
    )
  
    fmt2 = cellFormat(
        numberFormat=numberFormat('DATE', 'MM/DD/YYYY')
    )
  
    fmt_date_added = cellFormat(
        numberFormat=numberFormat('DATE', 'dddd, mmm dd, yyyy')
    )

    program_log("Header row", "formatted")
  
    format_cell_ranges(sheet, [
      ('A:M', format_row), 
      ('A1:M1', header_row), 
      ('A2:M', fmt), 
      ('A2:A', fmt2),
      ('J2:J', fmt2),
      ('M2:M', fmt_date_added),
      ('A1:M1', header_row)
      ])
  
  
    sheet.sort((1, 'des'))
    program_log("The spreadsheet", "sorted by date")
  
    sh.batch_update(body)
    program_log("New conditional formatting", "applied")
  
