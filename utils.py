import gspread
from gspread_formatting import *
from gspread_formatting import Color
from oauth2client.service_account import ServiceAccountCredentials
import utils
import pygsheets

def gspread_creds():
    scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name("driveapi.json", scopes)
    file = gspread.authorize(credentials)
    sheet = file.open("FlightPricing")
    sheet = sheet.sheet1

    return sheet, file

sheet, file = gspread_creds()

def format_sheet():
  spreadsheetId = "1JwAhe_dNRWQUnRm0c3y3_pWivcEMai_h9euNN2Mqy7w"  # Please set the Spreadsheet ID.
  sh = file.open_by_key(spreadsheetId)
  rules = get_conditional_format_rules(sheet)
  rules.clear()
  rules.save()
  
  formula = '=IF($L1:$L1<>"", $L:$L<1000, "Empty")'
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
                                  "green": 0.95,
                                  "red": 0.90,
                                  "blue": 0.95
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
    horizontalAlignment='CENTER'
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
  format_cell_range(sheet, 'A1:M1', header_row)
  format_cell_range(sheet, 'A2:M', fmt)

  format_cell_range(sheet, 'A2:A', fmt2)
  # format_cell_range(sheet, 'J2:J', fmt2)

  sheet.sort((1, 'asc'), range='A2:M1000')
  sh.batch_update(body)
