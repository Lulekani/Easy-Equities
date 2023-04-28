import base64
import sys
import traceback
import configparser
import time
import re

import pandas as pd

from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common import keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service


from webdriver_manager.firefox import GeckoDriverManager

from shutil import which

from urllib3.packages.six import b
from bs4 import BeautifulSoup

class EasyEquities:
    timeout = 2.5
    driver = None
    account = None
    options = None

    def __init__(self) -> None:
        pass

    def __init__(self, username, password, account = 'DEMO') -> None:
        self.options = FirefoxOptions()
        
        self.Username = username
        self.Password = password
        if account == 'DEMO':
            self.account = 'Demo ZAR'
        if account == 'ZAR':
            self.account = 'EasyEquities ZAR'

    def open(self):
        self.options.add_argument('--headless')
        self.driver = webdriver.Firefox(options=self.options, service=Service(GeckoDriverManager().install()))
        self.driver_wait = WebDriverWait(self.driver, 90)
        self.login(self.Username, self.Password)

    def close(self):
        time.sleep(self.timeout)
        self.logout()
        self.driver.close()
        
    def login(self, username, password):
        self.driver.get('https://identity.openeasy.io/Account/Login')
        self.driver_wait.until(EC.presence_of_element_located((By.ID, "SignIn")))
        self.driver.find_element(By.ID, 'user-identifier-input').send_keys(username)
        self.driver.find_element(By.ID,  'Password').send_keys(password)
        self.driver.find_element(By.ID, 'SignIn').click()

        time.sleep(self.timeout)
        if self.driver.current_url == 'https://identity.openeasy.io/Grants':
            self.driver.get('https://platform.easyequities.io/')

    def logout(self):
        self.driver.get('https://identity.openeasy.io/Account/Logout')
        self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, "btn-primary")))
        self.driver.find_elements(By.CLASS_NAME, "btn-primary")[1].click()

    def balance(self) -> dict:  
        self.open()  
        Balance = {}

        self.driver.get('https://platform.easyequities.io/AccountOverview')
        time.sleep(self.timeout)
        self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, "slick-track")))
        self.driver.find_elements(By.XPATH, "//*[text()='{0}']".format(self.account))[0].click()
        
        self.driver_wait.until(EC.presence_of_element_located((By.ID, "account-distribution")))
        time.sleep(self.timeout)
        balance = self.driver.find_element(By.ID, "asset-class-display")
        balance = pd.read_html(balance.get_attribute('innerHTML'))

        for item in balance:
            for i, row in item.iterrows():
                Balance[row[0]] = str(row[3])[1:].replace(' ', '')

        self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, "asset-summary-heading")))
        Summary = self.driver.find_elements(By.CLASS_NAME,  'asset-summary-heading')
        Balance['Value'] = Summary[0].text.replace('R', '').replace(' ', '')
        Balance['Movement'] = Summary[1].text.replace('R', '').replace(' ', '')
        Balance['Status'] = Summary[2].text[:-1].replace(' ', '')

        self.close()

        return Balance

    def holdings(self, tickers = True) -> list:
        self.open() 

        Holdings = []

        self.driver.get('https://platform.easyequities.io/AccountOverview')  
        time.sleep(self.timeout)
        self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, "slick-track")))
        self.driver.find_elements(By.XPATH, "//*[text()='{0}']".format(self.account))[0].click()
        time.sleep(self.timeout)
        self.driver_wait.until(EC.presence_of_element_located((By.ID, "loadHoldings")))
        self.driver.find_element(By.ID, "loadHoldings").click()

        try:
            self.driver_wait.until(EC.presence_of_element_located((By.ID, "no-holdings-message")))
            element = self.driver.find_element(By.ID, "no-holdings-message")
            if element is not None:
                self.close()
                return Holdings
        except:
            pass

        time.sleep(self.timeout)
        self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, "holding-table-body")))
        holdings_table = self.driver.find_element(By.CLASS_NAME, 'holding-table-body')
        tickers_data = holdings_table.find_elements(By.CLASS_NAME, 'content-box')

        for ticker in tickers_data:
            image = ticker.find_element(By.TAG_NAME, 'img').get_attribute('src')
            holding = str(image).split('.')[-2].upper()
            purchase = str(ticker.find_element(By.CLASS_NAME, 'purchase-value-cell').text)[1:].replace(' ', '')
            current = str(ticker.find_element(By.CLASS_NAME, 'current-value-cell').text)[1:].replace(' ', '')
            movement = str(ticker.find_element(By.CLASS_NAME, 'pnl-cell').text)

            Holdings.append({'Holding': holding,
                'Purchase': purchase,
                'Current': current,
                'Image': image,
                'Movement': movement})
            
        self.close()

        return Holdings

    def buy(self, ticker, shares = 1, amount = None, instruction = 'OPEN', limit = True, price = None):
        try:
            self.open()
            self.driver.get('https://platform.easyequities.io/ValueAllocation/Buy?contractCode=EQU.ZA.{0}'.format(ticker.upper()))
            self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, "slick-track")))
            self.driver.find_elements(By.XPATH, "//*[text()='{0}']".format(self.account))[0].click()   

            self.driver_wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "value-allocations__snapshot-price-request-loader")))
            self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, "flex-container")))
            if amount == None:
                self.driver.find_element(By.ID, 'js-number-of-shares').send_keys(keys.Keys.CONTROL, 'a')
                self.driver.find_element(By.ID, 'js-number-of-shares').send_keys(keys.Keys.BACKSPACE)
                self.driver.find_element(By.ID, 'js-number-of-shares').send_keys(shares)
                self.driver.find_element(By.ID, 'js-number-of-shares').send_keys(keys.Keys.ENTER)
                
            else:
                self.driver.find_element(By.ID, 'js-value-amount').send_keys(keys.Keys.CONTROL, 'a')
                self.driver.find_element(By.ID, 'js-value-amount').send_keys(keys.Keys.BACKSPACE)
                self.driver.find_element(By.ID, 'js-value-amount').send_keys(amount)        
                self.driver.find_element(By.ID, 'js-value-amount').send_keys(keys.Keys.ENTER)
            
            self.driver_wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "value-allocations__snapshot-price-request-loader")))
            self.driver_wait.until(EC.presence_of_element_located((By.ID, "netAmountDueDisplay")))

            if instruction != 'OPEN':
                self.driver.find_element(By.IDE, 'advanced-btn').click()
                if price != None:
                    self.driver.find_element(By.ID, 'OrderPrice').send_keys(keys.Keys.CONTROL, 'a')
                    self.driver.find_element(By.ID, 'OrderPrice').send_keys(keys.Keys.BACKSPACE)
                    self.driver.find_element(By.ID, 'OrderPrice').send_keys(price)
                    self.driver.find_element(By.ID, 'OrderPrice').send_keys(keys.Keys.ENTER)

            if limit == True:
                try:    
                    self.driver.find_elements(By.CLASS_NAME, 'btnTradeOrderType js-order-type-btn')[1].click()
                except:
                    pass

            time.sleep(self.timeout)
            self.driver.find_element(By.CLASS_NAME, 'trade-action-container__right-action-button').click()

            self.close()

            return True
        except Exception:
            traceback.print_exc()
            self.close()
            return False

    def sell(self, ticker, amount=None, percentage=100):
        try:
            self.open()
            self.driver.get('https://platform.easyequities.io/ValueAllocation/Sell?contractCode=EQU.ZA.{0}'.format(ticker.upper()))
            self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, "slick-track")))
            self.driver.find_elements(By.XPATH, "//*[text()='{0}']".format(self.account))[0].click()

            self.driver_wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "value-allocations__snapshot-price-request-loader")))
            self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, "flex-container")))
            element = self.driver.find_element(By.CLASS_NAME, 'flex-container')
            if element is not None:                
                if amount == None:
                    self.driver.find_element(By.ID, 'js-percentage-to-sell').send_keys(keys.Keys.CONTROL, 'a')
                    self.driver.find_element(By.ID, 'js-percentage-to-sell').send_keys(keys.Keys.BACKSPACE)
                    self.driver.find_element(By.ID, 'js-percentage-to-sell').send_keys(percentage)
                    self.driver.find_element(By.ID, 'js-percentage-to-sell').send_keys(keys.Keys.ENTER)
                else:   
                    self.driver.find_element(By.ID, 'js-value-amount').send_keys(keys.Keys.CONTROL, 'a')
                    self.driver.find_element(By.ID, 'js-value-amount').send_keys(keys.Keys.BACKSPACE)
                    self.driver.find_element(By.ID, 'js-value-amount').send_keys(amount)
                    self.driver.find_element(By.ID, 'js-value-amount').send_keys(keys.Keys.ENTER)
                
                self.driver_wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "value-allocations__snapshot-price-request-loader")))
                self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, "value-allocations__trade-button")))
                self.driver.find_element(By.CLASS_NAME, "value-allocations__trade-button").click()

                self.close()
                return True

            self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, "validation-summary-errors")))
            element = self.driver.find_element(By.CLASS_NAME, "validation-summary-errors")
            if element is not None:
                self.close()
                return False    
        except:
            traceback.print_exc()
            self.close()
            return False
            

if __name__ == '__main__':
    username = None
    password = None

    from yahoo_fin import stock_info as si
    import yfinance as yf

    try:
        username = ['Username']
        password = ['Password']
    except Exception as e:
        print("ERROR:\t{0}".format(e))
        sys.exit(1)
    finally:
        easy_equities = EasyEquities(username,  password, account='ZAR')

        print(easy_equities.holdings())
        for ticker in easy_equities.holdings():
            if easy_equities.sell(ticker.get('Holding')) == True:
                print(f"Sold {ticker.get('Holding')}")
            else:
                print(f"Failed to sell {ticker.get('Holding')}")
            exit()
    
        if easy_equities.buy('CPI', shares = 1) == True:
            print(f"Bought")
        else:
            print(f"Failed to buy")
        
        if easy_equities.sell('CPI') == True:
            print(f"Sold")
        else:
            print(f"Failed to sell")

        print(easy_equities.balance())

