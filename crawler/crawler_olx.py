from typing import List, Union

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from _common.database_communicator.tables import DataStagingCols
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

    def get_offer_urls(self, already_scraped_urls: List[str]) -> Union[List[str], bool]:
        offers = self.driver.find_elements(By.XPATH, "//a[@class='css-rc5s2u']")
        if not self.check_if_offers_loaded_properly(offers):
            return False

        offer_urls = []
        for offer in offers:
            href = offer.get_property('href')

            if href in self.main_scraped_urls:
                self.seen_records_from_db[DataStagingCols.URL].append(href)
                continue
            if href in already_scraped_urls:
                continue

            offer_urls.append(href)

        return offer_urls

    def extract_data_from_offer(self, offer_url: str) -> None:
        if 'olx' in offer_url:
            extractor = DataExtractorOLX(self.driver, self.scraped_records, page_to_extract_url=offer_url)
        elif 'otodom' in offer_url:
            extractor = DataExtractorOTODOM(self.driver, self.scraped_records, page_to_extract_url=offer_url)
        else:
            raise ValueError(f"Unknown domain for data extraction: {offer_url}")

        self.scraped_records = extractor.extract()
