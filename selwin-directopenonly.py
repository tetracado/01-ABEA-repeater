from selenium import webdriver
#from webdriver_manager.chrome import ChromeDriverManager
#from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import re

#options=Options()
#options.BinaryLocation='/usr/bin/chromium-browser'
#options.add_argument('--disable-infobars')
#options.add_argument('--disable-extensions')
#driver_path='/usr/bin/chromedriver'

driver = webdriver.Chrome(service=Service())
driver.set_window_position(0,0)
driver.set_window_size(768,1024)

def openlink(link):
    driver.get(link)
    time.sleep(5)

def savescnclose():
    scrname=str(str(int(time.time()))+".png")
    driver.save_screenshot(scrname)
    print('screenshot saved at',scrname)
    driver.close()

def savescn():
    scrname=str(str(int(time.time()))+".png")
    driver.save_screenshot(scrname)
    print('screenshot saved at',scrname)
    return scrname
