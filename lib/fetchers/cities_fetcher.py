from time import sleep

from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from lib.consts import DEFAULT_TIMEOUT, XPATHS, URLS
from lib.utils import get_driver


class CitiesFetcher:

    def __init__(self):
        self.driver = get_driver()
        self.wait = WebDriverWait(self.driver, DEFAULT_TIMEOUT)
        self.cities = {}

    def __close_subscription_overlay(self):

        # waits until it's visible
        self.wait.until(expected_conditions.visibility_of_element_located((By.XPATH, XPATHS['subscription-modal'])))

        # close it
        close_xpath = XPATHS['close-subscription-modal']
        # there's a div that sometimes gets in the way of the close button immediately after loading
        # waiting until it's clickable
        close_overlay_elem = (By.XPATH, close_xpath)
        close_overlay_link = self.wait.until(expected_conditions.element_to_be_clickable(close_overlay_elem))

        while True:
            try:
                close_overlay_link.click()
                self.wait.until(expected_conditions.invisibility_of_element_located((By.XPATH, XPATHS['subscription-modal'])))
                break
            except TimeoutException as timeout:
                # something went wrong while waiting for modal to go away
                # retries closing link
                close_overlay_link.click()
            except WebDriverException as ex:
                # something went wrong trying to click the close button
                self.wait.until(expected_conditions.element_to_be_clickable(close_overlay_elem))

    def __open_geolocation_modal(self):
        geolocation_button = self.driver.find_element_by_xpath(XPATHS['geolocation_button'])
        geolocation_button.click()
        # waits until geolocation modal becomes visible
        geolocation_modal = self.driver.find_element_by_xpath(XPATHS['geolocation_modal'])
        self.wait.until(expected_conditions.visibility_of(geolocation_modal))

    def __parse_cities(self, state):
        while True:
            city_select = self.driver.find_element_by_xpath(XPATHS['city_select'])

            # turns out cities aren't immediately populated
            # hold this loop until all options are available
            options_count = len(city_select.find_elements_by_xpath(".//*"))

            if options_count > 1:
                break
            else:
                # NOTE: can't use driver's wait here as it needs a known element to expect
                sleep(0.3)

        cities_html = city_select.get_attribute('innerHTML')

        # parses city options
        city_parser = BeautifulSoup(cities_html, 'html.parser')

        cities = city_parser.contents
        for city_option in cities:
            city_name = city_option.text
            # seems redundant but will help convert this dict to a csv row transparently
            self.cities[city_name] = {}
            self.cities[city_name]['name'] = city_name
            self.cities[city_name]['city_id'] = city_option.attrs['value']  # climatempo id for this city
            self.cities[city_name]['state'] = state

    def __parse_states(self):
        self.states = {}

        state_select = self.driver.find_element_by_xpath(XPATHS['state_select'])
        state_select_component = Select(state_select)  # makes it easier to swap states
        states_html = state_select.get_attribute('innerHTML')

        # parses state options
        state_parser = BeautifulSoup(states_html, 'html.parser')

        for state_option in state_parser.contents:
            state = state_option.text
            # selects a state to show it's cities
            state_select_component.select_by_visible_text(state)

            self.__parse_cities(state)

    def fetch(self):
        self.driver.get(URLS['cities_fetch'])  # retrieves page where cities are listed

        # NOTE: there's a pesky subscription overlay that takes over (grabbing focus)
        self.__close_subscription_overlay()

        # a per state city list is hidden behind a js button that triggers a modal
        self.__open_geolocation_modal()

        # at this point both select elements (for states and cities) should be visible
        self.__parse_states()

        self.driver.close()  # releasing chrome

        return self.cities
