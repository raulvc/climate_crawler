# Climate Crawler
Spider for www.climatempo.com.br developed as an exercise project in Python.

Extracts climate data for (available) brazilian cities and exports in tabular format (csv).

# Dependencies
- python3 (>= 3.3)
- chromedriver (http://chromedriver.chromium.org/)
- python-selenium (https://pypi.org/project/selenium/)
- python-beautifulsoup4 (https://pypi.org/project/beautifulsoup4/)

# Usage
```
$ python3 crawler.py --help
usage: crawler.py [-h] [-l LIMIT] [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -l LIMIT, --limit LIMIT
                        limit of climate fetch requests
  -o OUTPUT, --output OUTPUT
                        output filepath
```
Defaults are:
- limit: infinity
- output: 'export.csv' in current working directory

# Examples
`$ python3 crawler.py -l 100`

stdout:
```
Started at 2018-05-26 23:59:27.077283
Climate fetch requests limit: 100
Output data to '/home/raul/projs/climate_crawler/export.csv'
Retrieving available cities...
Found 5722 cities
Done. (0:00:54.811614)
Retrieving weather data...
(1/100) Scraping Abadia de Goiás - Goiás...
[...]
(100/100) Scraping Almadina - Bahia...
Done. (0:15:52.250898)
Writing data to disk in csv format...
Done. (0:00:00.000344)
Total time: 0:16:47.062856
```

file output:
[export.csv](https://github.com/raulvc/climate_crawler/blob/master/export.csv)