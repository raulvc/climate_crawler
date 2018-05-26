DEFAULT_TIMEOUT = 30  # 30s timeout for selenium requests
URLS = {
    'br_cities': 'https://www.climatempo.com.br/brasil'
}
XPATHS = {
    'subscription-modal': '//div[@id="modal-subscribe" and @role="dialog"]',
    'close-subscription-modal': '//a[@id="closeButton" and @class="modal-color-climatempo"]',
    'geolocation_button': '//h1[@id="momento-localidade"]',
    'geolocation_modal': '//div[@id="geolocation" and @class="modal modal-geo open"]',
    'state_select': '//select[@id="sel-state-geo" and @class="slt-geo"]',
    'city_select': '//select[@id="sel-city-geo" and @class="slt-geo"]'
}