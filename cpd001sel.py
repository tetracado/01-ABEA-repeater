from selenium import webdriver
import platform
#from webdriver_manager.chrome import ChromeDriverManager
#from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import re
import os

mydir=os.path.dirname(__file__)

options=Options()
options.add_argument('--disable-infobars')
options.add_argument('--disable-extensions')
options.add_argument('--disable-gpu')
#options.add_argument('--headless')
options.add_argument('--window-size=1024,1068')

scroptions=webdriver.ChromeOptions()
scroptions.headless = True
if platform.system() == "Linux":
     #if raspi
    service = webdriver.ChromeService(executable_path="/usr/bin/chromedriver")
else: # if not raspi and considering you're using Chrome
    service = webdriver.ChromeService()

driver = webdriver.Chrome(options=options,service=service)
scrdriver = webdriver.Chrome(options=scroptions,service=service)

def openlink(link):
    print('opening:',link)
    driver.get(link)
    time.sleep(5)

def savescn(link):
    scrname=str(str(int(time.time()))+".png")
    scrpath=os.path.join(mydir,'img',scrname)

    print('about to save screenshot at:',scrpath)

    #create new webdriver to avoid limiting screenshots
    # https://stackoverflow.com/questions/41721734/take-screenshot-of-full-page-with-selenium-python-with-chromedriver/57338909#57338909

    #scrdriver = webdriver.Chrome(options=scroptions,service=service)
    scrdriver.get(link)
    scrhelp=lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
    scrdriver.set_window_size(scrhelp('Width'),scrhelp('Height')) # May need manual adjustment
    screlement=scrdriver.find_element(By.TAG_NAME, "main")
    screlement.screenshot(scrpath)
    #scrdriver.close()

    #driver.save_screenshot(scrpath)
    #driver.find_element_by_tag_name('body').screenshot(scrpath)
    print('screenshot saved at',scrpath)
    return scrpath    


def refreshcheck():
    print('refreshing abea')
    driver.get("https://emergencyalert.alberta.ca/")
