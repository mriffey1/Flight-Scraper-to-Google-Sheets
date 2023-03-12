from selenium.webdriver.chrome.service import Service
from selenium import webdriver

def web_driver(src: str):
    s = Service("C:\Windows\chromedriver.exe")
    driver = webdriver.Chrome(service=s)
    driver.maximize_window()
    driver.get(src)

    return driver