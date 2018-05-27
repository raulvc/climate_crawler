import argparse
import csv
import os
from datetime import datetime
from math import inf as infinity

from multiprocessing import Pool, cpu_count

from lib.consts import *
from lib.fetchers.cities_fetcher import CitiesFetcher
from lib.fetchers.climate_fetcher import ClimateFetcher


class Crawler:

    def __init__(self, output_file, limit):
        self.output_file = output_file
        self.limit = limit

    def __fetch_available_cities(self):
        cities_fetcher = CitiesFetcher()
        self.cities = cities_fetcher.fetch()

    def __get_process_queue(self):
        # prepares args
        queue = []
        count = 1
        # iterates over cities in alphabetical order
        for city_name in sorted(self.cities.keys()):
            city_data = self.cities[city_name]
            queue.append(city_data)
            count += 1
            if count > self.limit:
                break

        # zip is a python 3 helper to convert structures to tuples (that's the multiprocessing way of sending args)
        # the range function in zip's arguments appends a sequential number to tuple args
        return zip(queue, range(1, len(queue) + 1))

    def __load_data(self):
        city_count = len(self.cities)
        # upper boundary
        upper_limit = min(city_count, self.limit)

        # parallelizes climate fetch
        climate_fetcher = ClimateFetcher(upper_limit)
        process_queue = self.__get_process_queue()
        with Pool(cpu_count() - 1) as pool:  # uses all available cores except 1
            results = pool.starmap(climate_fetcher.fetch, process_queue)
        pool.close()
        pool.join()  # waits until every thread returns
        self.processed_cities = results  # pool keeps results sorted

    def __dump_data(self):
        if os.path.exists(self.output_file):
            print('[WARN] "%s" exists already. Will be overwritten.' % self.output_file)

        try:
            with open(self.output_file, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(COLUMNS)
                for city_data in self.processed_cities:
                    writer.writerow(city_data.values())
        except IOError as ex:
            print("Couldn't write to %s:" % self.output_file)
            print(ex.strerror)
            exit(1)

    def start(self):
        start_time = datetime.now()
        print('Started at %s' % start_time)
        if self.limit == infinity:
            print('Running in unlimited mode (fetches all available cities)')
        else:
            print('Climate fetch requests limit: %s' % self.limit)
        print("Output data to '%s'" % self.output_file)

        # retrieves available states and cities and stores it in an instance var 'states'
        print('Retrieving available cities...')
        self.__fetch_available_cities()
        fetch_cities_time = datetime.now()
        print('Found %s cities' % len(self.cities))
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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--limit', type=int, help='limit of climate fetch requests', default=infinity)
    parser.add_argument('-o', '--output', type=str, help='output filepath', default=os.path.join(os.getcwd(), 'export.csv'))
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    crawler = Crawler(limit=args.limit, output_file=args.output)
    crawler.start()
