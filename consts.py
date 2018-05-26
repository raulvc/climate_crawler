DEFAULT_TIMEOUT = 30  # 30s timeout for selenium requests
URLS = {
    'cities_fetch': 'https://www.climatempo.com.br/brasil',
    'climate_fetch': 'https://www.climatempo.com.br/previsao-do-tempo/cidade/'
}
XPATHS = {
    'subscription-modal': '//div[@id="modal-subscribe" and @role="dialog"]',
    'close-subscription-modal': '//a[@id="closeButton" and @class="modal-color-climatempo"]',
    'geolocation_button': '//h1[@id="momento-localidade"]',
    'geolocation_modal': '//div[@id="geolocation" and @class="modal modal-geo open"]',
    'state_select': '//select[@id="sel-state-geo" and @class="slt-geo"]',
    'city_select': '//select[@id="sel-city-geo" and @class="slt-geo"]',
    'main_container': '//div[@id="mega-destaque" and @data-id="mainContainer"]'
}
COLUMNS = ['city_id', 'state', 'min_temp', 'max_temp', 'precipitation', 'month']
