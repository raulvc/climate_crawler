import shutil  # NOTE: python >= 3.3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from consts import *


class Crawler:

    def __init__(self):
        self.driver = self.__get_driver()
        self.driver.implicitly_wait(DEFAULT_TIMEOUT)
        self.wait = WebDriverWait(self.driver, DEFAULT_TIMEOUT)

    @staticmethod
    def __get_chromedriver_path():
        # finds out path of chromedriver (just like the 'which' command in linux systems)
        bin_names = ['chromedriver-dev', 'chromedriver']  # uses dev channel of the driver package if available
        path = ''
        for bin_name in bin_names:
            path = shutil.which(bin_name)
            if path:
                break
        return path

    def __get_driver(self):
        # emulates chrome
        options = webdriver.ChromeOptions()
        # using headless mode for better performance
        options.add_argument('--headless')
        driver = webdriver.Chrome(self.__get_chromedriver_path(), chrome_options=options)
        return driver

    def __close_subscription_overlay(self):

        # waits until it's visible
        self.wait.until(expected_conditions.visibility_of(self.driver.find_element_by_id('modal-subscribe')))

        # close it
        close_xpath = XPATHS['close-subscription-modal']
        # there's a div that sometimes get in the way of the close button immediately after loading
        # waiting until it's clickable
        close_overlay_link = self.wait.until(expected_conditions.element_to_be_clickable((By.XPATH, close_xpath)))
        close_overlay_link.click()

    def __parse_cities(self, state):
        city_select = self.driver.find_element_by_xpath(XPATHS['city_select'])
        cities_html = city_select.get_attribute('innerHTML')

        # parses city options
        city_parser = BeautifulSoup(cities_html, 'html.parser')

        for city_option in city_parser.contents:
            self.states[state]['cities'].append(city_option.text)

    def __parse_states(self):
        self.states = {}

        state_select = self.driver.find_element_by_xpath(XPATHS['state_select'])
        state_select_component = Select(state_select)  # makes it easier to swap states
        states_html = state_select.get_attribute('innerHTML')

        # parses state options
        state_parser = BeautifulSoup(states_html, 'html.parser')

        for state_option in state_parser.contents:
            state = state_option.text
            self.states[state] = {'cities': []}

            # selects a state to show it's cities
            state_select_component.select_by_visible_text(state)

            self.__parse_cities(state)

    def __fetch_available_cities(self):
        self.driver.get(URLS['br_cities'])  # retrieves page where cities are listed

        # NOTE: there's a pesky subscription overlay that takes over (grabbing focus)
        self.__close_subscription_overlay()

        # a per state city list is hidden behind a js button that triggers a modal
        geolocation_button = self.driver.find_element_by_xpath(XPATHS['geolocation_button'])
        geolocation_button.click()
        # waits until geolocation modal becomes visible
        geolocation_modal = self.driver.find_element_by_xpath(XPATHS['geolocation_modal'])
        self.wait.until(expected_conditions.visibility_of(geolocation_modal))

        # at this point both select elements (for states and cities) should be visible
        self.__parse_states()

    def start(self):
        self.__fetch_available_cities()


if __name__ == '__main__':
    crawler = Crawler()
    crawler.start()
