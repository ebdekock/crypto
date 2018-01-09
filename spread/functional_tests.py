from django.conf import settings
from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Create site URL for tests
site_url = 'http://' + settings.SITE_URL + ":" + settings.SITE_PORT

class BrowserTest(TestCase):

    def setUp(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')
        self.dc = DesiredCapabilities.CHROME
        self.dc['loggingPrefs'] = { 'browser':'ALL' }
        self.browser = webdriver.Chrome(chrome_options=self.options, desired_capabilities=self.dc)

    def tearDown(self):
        self.browser.quit()

    def test_site_sections_loaded(self):
        self.browser.get(site_url)
        test_headers = ['Price', 'Volume', 'Latest Arb', 'Average Arb']
        site_headers = []
        site_header_objects = self.browser.find_elements_by_tag_name('h4')
        for site_header in site_header_objects:
            site_headers.append(site_header.text)
        self.assertCountEqual(test_headers, site_headers)

    def test_for_console_errors(self):
        self.browser.get(site_url)
        for log_entry in self.browser.get_log('browser'):
            self.assertNotIn('console-api', log_entry['source'], log_entry)
