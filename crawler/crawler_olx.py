from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from crawler.crawler_base import CrawlerBase
from crawler.data_extractors.extractor_olx import DataExtractorOLX
from crawler.data_extractors.extractor_otodom import DataExtractorOTODOM


class CrawlerOLX(CrawlerBase):
    START_PAGES = ['https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/poznan/q-nieruchomości/',
                   'https://www.olx.pl/nieruchomosci/domy/sprzedaz/poznan/q-nieruchomości/']

    def __init__(self):
        super().__init__()

    def enter_start_page(self, url: str) -> None:
        self.driver.get(url)
        self.sleep_random_seconds(_from=2, to=4)
        self.click_button_with_text(text='Akceptuję')

    def get_next_page_arrow(self) -> WebElement:
        return self._find_element(By.XPATH, "//a[@data-testid='pagination-forward']")

    def get_offer_urls(self, already_scraped_urls: List[str]) -> List[str]:
        offers = self.driver.find_elements(By.XPATH, "//a[@class='css-rc5s2u']")
        offer_urls = [offer.get_property('href') for offer in offers
                      if offer.get_property('href') not in already_scraped_urls]

        return offer_urls

    def extract_data_from_offer(self, offer_url: str) -> None:
        if 'olx' in offer_url:
            extractor = DataExtractorOLX(self.driver, self.scraped_records, page_to_extract_url=offer_url)
        elif 'otodom' in offer_url:
            extractor = DataExtractorOTODOM(self.driver, self.scraped_records, page_to_extract_url=offer_url)
        else:
            raise ValueError(f"Unknown domain for data extraction: {offer_url}")

        self.scraped_records = extractor.extract()