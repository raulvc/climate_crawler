import shutil  # NOTE: python >= 3.3

from selenium import webdriver

from lib.consts import DEFAULT_TIMEOUT


def get_driver():
    # emulates chrome
    options = webdriver.ChromeOptions()
    # using headless mode for better performance
    options.add_argument('--headless')
    driver = webdriver.Chrome(get_chromedriver_path(), chrome_options=options)
    driver.implicitly_wait(DEFAULT_TIMEOUT)
    return driver


def get_chromedriver_path():
    # finds out path of chromedriver (just like the 'which' command in linux systems)
    bin_names = ['chromedriver-dev', 'chromedriver']  # uses dev channel of the driver package if available
    path = ''
    for bin_name in bin_names:
        path = shutil.which(bin_name)
        if path:
            break
    return path
