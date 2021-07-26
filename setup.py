from distutils.core import setup
setup(
  name = 'EasyEquities',         # How you named your package folder (MyLib)
  packages = ['EasyEquities'],   # Chose the same as "name"
  version = '1.0.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'EasyEquities active scraper to issue trading instructions',   # Give a short description about your library
  author = 'Kloniphani Maxakadzi',                   # Type in your name
  author_email = 'Kloniphani@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/kloniphani/EasyEquities',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/kloniphani/EasyEquities/archive/refs/tags/v1.0.tar.gz',    # I explain this later on
  keywords = ['South Africa', 'Trading', 'EasyEQuities'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'validators',
          'beautifulsoup4',
          'selenium',
          'urllib3',
          'webdriver_manager',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
  ],
)