import csv
import os
import shutil  # NOTE: python >= 3.3
from datetime import datetime
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from consts import *


class Crawler:

    def __init__(self, output_file=None, limit=10):
        self.output_file = output_file
        self.limit = limit
        self.driver = self.__get_driver()
        self.driver.implicitly_wait(DEFAULT_TIMEOUT)
        self.wait = WebDriverWait(self.driver, DEFAULT_TIMEOUT)
        self.cities_count = 0

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
        self.wait.until(expected_conditions.visibility_of_element_located((By.XPATH, XPATHS['subscription-modal'])))

        # close it
        close_xpath = XPATHS['close-subscription-modal']
        # there's a div that sometimes gets in the way of the close button immediately after loading
        # waiting until it's clickable
        close_overlay_link = self.wait.until(expected_conditions.element_to_be_clickable((By.XPATH, close_xpath)))
        close_overlay_link.click()

        while True:
            try:
                self.wait.until(expected_conditions.invisibility_of_element_located((By.XPATH, XPATHS['subscription-modal'])))
                break
            except TimeoutException as timeout:
                # something went wrong while waiting for modal to go away
                # retries closing link
                close_overlay_link.click()

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
        self.cities_count += len(cities)  # to keep a count of total cities
        for city_option in cities:
            city_name = city_option.text
            city_id = city_option.attrs['value']  # climatempo id for this city
            self.states[state][city_name] = {}
            self.states[state][city_name]['city_id'] = city_id

    def __parse_states(self):
        self.states = {}

        state_select = self.driver.find_element_by_xpath(XPATHS['state_select'])
        state_select_component = Select(state_select)  # makes it easier to swap states
        states_html = state_select.get_attribute('innerHTML')

        # parses state options
        state_parser = BeautifulSoup(states_html, 'html.parser')

        for state_option in state_parser.contents:
            state = state_option.text
            self.states[state] = {}

            # selects a state to show it's cities
            state_select_component.select_by_visible_text(state)

            self.__parse_cities(state)

    def __fetch_available_cities(self):
        self.driver.get(URLS['cities_fetch'])  # retrieves page where cities are listed

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

    @staticmethod
    def __parse_precipitation(raw_precipitation):
        return raw_precipitation.split('\n')[0] + ' mm'

    @staticmethod
    def __parse_month(raw_date):
        date_segment = raw_date[-5:]  # extracts the 'dd/mm' part of the string
        date_obj = datetime.strptime(date_segment, '%d/%m')  # converts to a date object
        return datetime.strftime(date_obj, '%b')  # returns month's full name from current locale

    def __load_city_climate(self, state, city):
        city_data = self.states[state][city]
        city_data['state'] = state  # seems redundant but avoids adding this field later in csv writer

        self.driver.get(URLS['climate_fetch'] + city_data['city_id'])  # specific page for this city

        # finds container for current weather
        main_container = self.driver.find_element_by_xpath(XPATHS['main_container'])
        main_container_html = main_container.get_attribute('innerHTML')

        # parses weather data
        weather_parser = BeautifulSoup(main_container_html, 'html.parser')

        # temperatures
        city_data['min_temp'] = weather_parser.find(id='tempMin0').text
        city_data['max_temp'] = weather_parser.find(id='tempMax0').text

        # precipitation
        raw_precipitation = weather_parser.findAll('p', {'arial-label': 'ícone do tempo Manhã'})[0].text
        city_data['precipitation'] = self.__parse_precipitation(raw_precipitation)

        # date
        # NOTE: honestly we could just grab current date from system, but in the odd scenario where
        # climatempo is on a weird offset this works fine
        raw_date = weather_parser.find(lambda tag: tag.name == 'h1' and 'PREVISÃO DE HOJE' in tag.text).text
        city_data['month'] = self.__parse_month(raw_date)

        # committing weather data to city's dict
        self.states[state][city] = city_data

    def __load_data(self):
        # iterates over states and cities in alphabetical order
        count = 1
        for state in sorted(self.states.keys()):
            cities = sorted(self.states[state].keys())
            for city in cities:
                print('(%s/%s) Scraping %s - %s...' % (count, self.cities_count, state, city))
                self.__load_city_climate(state, city)
                count += 1
                if count > self.limit:
                    print('[WARN] Reached defined limit of %s cities' % self.limit)
                    return

    def __dump_data(self, output_file=None):
        if not output_file:
            output_file = os.path.join(os.getcwd(), 'climate_export.csv')
        if os.path.exists(output_file):
            print('[WARN] "%s" exists already. Will be overwritten.' % output_file)

        with open(output_file, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(COLUMNS)

            # iterates over states and cities in alphabetical order
            count = 1
            for state in sorted(self.states.keys()):
                cities = sorted(self.states[state].keys())
                for city in cities:
                    city_data = self.states[state][city]
                    writer.writerow(city_data.values())
                    count += 1
                    if count > self.limit:
                        return

    def start(self):
        start_time = datetime.now()

        # retrieves available states and cities and stores it in an instance var 'states'
        print('Retrieving available cities...')
        self.__fetch_available_cities()
        fetch_cities_time = datetime.now()
        print('Found %s cities' % self.cities_count)
        print('Done. (%s)' % (fetch_cities_time - start_time))

        # iterates over all cities, loading pages and retrieving data
        print('Retrieving weather data...')
        self.__load_data()
        load_data_time = datetime.now()
        print('Done. (%s)' % (load_data_time - fetch_cities_time))

        # dumps in memory data to disk
        print('Writing data to disk in csv format...')
        self.__dump_data()
        end_time = datetime.now()
        print('Done. (%s)' % (end_time - load_data_time))

        print('Total time: %s' % (end_time - start_time))


if __name__ == '__main__':
    crawler = Crawler()
    crawler.start()
