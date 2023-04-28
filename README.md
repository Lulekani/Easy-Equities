# [EasyEquities](https://www.easyequities.co.za/) Python Package
This is a Python package for interacting with the [EasyEquities](https://www.easyequities.co.za/) trading platform. It provides a simple way to log in, check account balances, and retrieve your holdings.

## Requirements
- Python 3.x
- Selenium
- pandas
- Beautiful Soup 4
- GeckoDriverManager
- Firefox

## Installation
To install, run:
```bash
pip install pandas selenium webdriver_manager beautifulsoup4
```
Then, install the package from PIP using:
```bash
pip install easyequities
```

## Usage
To use the package, you will need to import the package and create an instance of the EasyEquities class. You will need to provide your username and password as arguments. You can then use the `balance` and `holdings` methods to obtain your account balance and holdings, respectively. 

Here's an example of how to use the scraper:
```python
from easyequities import EasyEquities
# Instantiate the EasyEquities class with your account credentials
ee = EasyEquities('your_username', 'your_password')

# Get your account balance
balance = ee.balance()
print(balance)

# Get your holdings
holdings = ee.holdings()
print(holdings)

# Close the EasyEquities website
ee.close()
```

Note that the script uses Firefox as the web driver, so you'll need to have Firefox installed on your machine for it to work. If you don't have Firefox installed, you can download it [here](https://www.mozilla.org/en-US/firefox/new/).

## License
This code is licensed under the MIT License. See the [LICENSE](https://github.com/kloniphani/EasyEquities/blob/main/LICENSE). Feel free to use it for any purpose.

# Disclaimers
Before you start using the code, a few disclaimers:
- This code does not come with any guarantee or warranty.
- I am not a financial advisor. This work does not represent any financial advice.
- I do not recommend the use of this code for any investment decisions.
- This code is designed for personal use, and is not designed for high-volume extractions.
- Use the code at your own risk.