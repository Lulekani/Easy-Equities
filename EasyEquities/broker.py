import base64
import sys
import traceback
import configparser
import time
import re
from requests.api import options

from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from urllib3.packages.six import b
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup

class EasyEquities:
    timeout = 3
    driver = None
    account = None
    options = None

    def __init__(self) -> None:
        pass

    def __init__(self, username, password, account = 'DEMO') -> None:
        self.Username = username
        self.Password = password
        if account == 'DEMO':
            self.account = 'slick-slide04'
        if account == 'ZAR':
            self.account = 'slick-slide00'
        self.options = Options()


    def open(self):
        self.options.headless = True
        self.driver = webdriver.Firefox(
            options = self.options,
            executable_path=GeckoDriverManager().install())
        self.driver_wait = WebDriverWait(self.driver, 90)
        self.login(self.Username, self.Password)

    def close(self):
        time.sleep(self.timeout)
        self.driver.close()
        
    def login(self, username, password):
        self.driver.get('https://platform.easyequities.io/Account/SignIn')
        self.driver_wait.until(EC.presence_of_element_located((By.ID, "login-mobile")))
        self.driver.find_element_by_id('user-identifier-input').send_keys(username)
        self.driver.find_element_by_id('Password').send_keys(password)
        self.driver.find_element_by_id('login-mobile').click()

    def balance(self):  
        self.open()      
        self.driver_wait.until(EC.presence_of_element_located(
            (By.ID, "important-documents")))
        self.driver.get('https://platform.easyequities.io/AccountOverview')
        time.sleep(self.timeout)
        self.driver.find_elements_by_xpath(
            "//div[ @aria-describedby='{0}']".format(self.account))[0].click()
        self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, "funds-to-invest")))
        balance = self.driver.find_elements_by_xpath("//div[ @aria-describedby='{0}']".format(self.account))[0]
        balance = balance.text.split('\n')[-1][1:].replace(' ', '')
        
        self.close()

        return balance

    def holdings(self, tickers = True):
        self.open()        
        Holdings = []

        self.driver_wait.until(EC.presence_of_element_located((By.ID, "important-documents")))
        self.driver.get('https://platform.easyequities.io/AccountOverview')  
        self.driver.find_element_by_xpath("//div[@aria-describedby='{0}']".format(self.account)).click()
        self.driver_wait.until(EC.presence_of_element_located((By.ID, "loadHoldings")))
        self.driver.find_element_by_id('loadHoldings').click()
        self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, "holding-table-body")))
        holdings_data = self.driver.find_element_by_class_name('holding-table-body')
        ticker_info = holdings_data.get_attribute('innerHTML')
        
        soup = BeautifulSoup(ticker_info, 'lxml')
        ticker_table = soup.findAll('div', attrs={"class": "table-display"})
        if(tickers):
            for link in soup.findAll('a', href=True, text=True, attrs={"class": "btn"}):
                ticker = link['href'].split('.')[-1]
                if ticker not in Holdings:
                    Holdings.append(ticker)
        else:
            for ticker in ticker_table:  
                ticker = str("".join([ll.strip() for ll in ticker.text.splitlines() if ll.strip()]))            
                regex =  r'([R]\d+\.?\d*)'
                ticker = re.split(regex, ticker)
                if ticker is not None:
                    try:
                        Holdings.append((ticker[0], ticker[1]))
                    except:
                        continue

        self.close()

        return Holdings

    def buy(self, ticker, shares = 1, amount = None):
        self.open()

        self.driver_wait.until(EC.presence_of_element_located((By.ID, "important-documents")))
        self.driver.get('https://platform.easyequities.io/Equity')  
        time.sleep(self.timeout)
        self.driver.find_elements_by_xpath("//div[ @aria-describedby='{0}']".format(self.account))[0].click()
        time.sleep(self.timeout-2)
        self.driver.find_element_by_id('InstrumentSearchString').send_keys(ticker)
        time.sleep(self.timeout-2)
        self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hoverBorder")))
        self.driver.get('https://platform.easyequities.io/ValueAllocation/Buy?contractCode=EQU.ZA.{0}'.format(ticker.upper()))
        time.sleep(self.timeout-2)

        self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tab-pane")))
        if amount == None:
            self.driver.find_element_by_id('js-number-of-shares').send_keys(keys.Keys.CONTROL, 'a')
            self.driver.find_element_by_id('js-number-of-shares').send_keys(keys.Keys.BACKSPACE)
            self.driver.find_element_by_id('js-number-of-shares').send_keys(shares)
            time.sleep(self.timeout)
            self.driver.find_element_by_class_name('flex-container').click()
        else:
            self.driver.find_element_by_id('js-value-amount').send_keys(keys.Keys.CONTROL, 'a')
            self.driver.find_element_by_id('js-value-amount').send_keys(keys.Keys.BACKSPACE)
            self.driver.find_element_by_id('js-value-amount').send_keys(amount)        
            time.sleep(self.timeout)
            self.driver.find_element_by_class_name('flex-container').click()

        time.sleep(self.timeout)
        self.driver_wait.until(EC.presence_of_element_located((By.ID, "netAmountDueDisplay")))
        self.driver.find_element_by_class_name('trade-action-container__right-action-button').click()

        self.close()


    def sell(self, ticker, amount=None, percentage=100):
        self.open()

        self.driver_wait.until(EC.presence_of_element_located(
            (By.ID, "important-documents")))
        self.driver.get('https://platform.easyequities.io/AccountOverview')
        time.sleep(self.timeout)
        self.driver.find_elements_by_xpath(
            "//div[@aria-describedby='{0}']".format(self.account))[0].click()
        time.sleep(self.timeout-2)
        self.driver.get('https://platform.easyequities.io/ValueAllocation/Sell?contractCode=EQU.ZA.{0}'.format(ticker.upper()))
        time.sleep(self.timeout-2)
        
        if amount == None:
            self.driver.find_element_by_id('js-percentage-to-sell').send_keys(keys.Keys.CONTROL, 'a')
            self.driver.find_element_by_id('js-percentage-to-sell').send_keys(keys.Keys.BACKSPACE)
            self.driver.find_element_by_id('js-percentage-to-sell').send_keys(percentage)
            time.sleep(self.timeout)
            self.driver.find_element_by_class_name('value-allocations__enter-value-container').click()
        else:   
            self.driver.find_element_by_id('js-value-amount').send_keys(keys.Keys.CONTROL, 'a')
            self.driver.find_element_by_id('js-value-amount').send_keys(keys.Keys.BACKSPACE)
            self.driver.find_element_by_id('js-value-amount').send_keys(amount)
            time.sleep(self.timeout)
            self.driver.find_element_by_class_name('value-allocations__enter-value-container').click()

        time.sleep(self.timeout)
        self.driver_wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "chartjs-render-monitor")))
        self.driver.find_element_by_class_name(
            'value-allocations__trade-button').click()

        self.close()


if __name__ == '__main__':
    username = 'kloniphani'
    password = '~W0nd3r!'

    easy_equities = EasyEquities(username,  password, account='DEMO')
    #for ticker in easy_equities.holdings():
        #easy_equities.sell(ticker)
    #easy_equities.buy('CPI', shares = 7)
    #easy_equities.sell('CPI')
    print(easy_equities.balance())


