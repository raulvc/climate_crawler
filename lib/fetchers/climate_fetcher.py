from datetime import datetime

from bs4 import BeautifulSoup

from lib.consts import URLS, XPATHS
from lib.utils import get_driver


class ClimateFetcher:

    def __init__(self, upper_limit):
        self.upper_limit = upper_limit

    @staticmethod
    def __parse_precipitation(raw_precipitation):
        return raw_precipitation.split('\n')[0] + ' mm'

    @staticmethod
    def __parse_month(raw_date):
        date_segment = raw_date[-5:]  # extracts the 'dd/mm' part of the string
        date_obj = datetime.strptime(date_segment, '%d/%m')  # converts to a date object
        return datetime.strftime(date_obj, '%b')  # returns month's full name from current locale

    def __load_city_climate(self, driver, city_data):
        driver.get(URLS['climate_fetch'] + city_data['city_id'])  # specific page for this city

        # finds container for current weather
        main_container = driver.find_element_by_xpath(XPATHS['main_container'])
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

        return city_data

    def fetch(self, city_data, order):
        # NOTE: print is thread safe on python 3
        print('(%s/%s) Scraping %s - %s...' % (order, self.upper_limit, city_data['name'], city_data['state']))

        # NOTE: can't use this driver var as an instance variable due to multiprocessing limitations
        driver = get_driver()
        city_data = self.__load_city_climate(driver, city_data)
        driver.close()
        return city_data

