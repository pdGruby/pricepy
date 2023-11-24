from typing import Union

import re

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver

from crawler.common.selenium_common_methods import SeleniumCommonMethods


class ExtractorBase(SeleniumCommonMethods):
    def __init__(self, driver: WebDriver, scraped_records: dict, page_to_extract_url: str):
        self.driver = driver
        self.scraped_records = scraped_records
        self.page_to_extract_url = page_to_extract_url

    def read_data_box(self, regexes: dict, data_box: Union[WebElement, None]) -> None:
        if data_box is None:
            for colname in regexes.keys():
                self.scraped_records[colname].append(None)
            return

        data_box = data_box.text.lower()
        for colname, regex in regexes.items():
            found_value = re.search(regex, data_box)

            if found_value:
                self.scraped_records[colname].append(found_value.group(1))
            else:
                self.scraped_records[colname].append(None)
