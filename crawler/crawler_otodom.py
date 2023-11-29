from typing import List, Union

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from crawler.crawler_base import CrawlerBase
from crawler.data_extractors.extractor_otodom import DataExtractorOTODOM


class CrawlerOTODOM(CrawlerBase):
    START_PAGES = ['https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/wielkopolskie/poznan/poznan/poznan?ownerType' +
                   'SingleSelect=ALL&by=DEFAULT&direction=DESC&viewType=listing',
                   'https://www.otodom.pl/pl/wyniki/sprzedaz/dom/wielkopolskie/poznan/poznan/poznan?ownerTypeSingle' +
                   'Select=ALL&by=DEFAULT&direction=DESC&viewType=listing']

    def __init__(self):
        super().__init__()

    def enter_start_page(self, url: str) -> None:
        self.driver.get(url)
        self.sleep_random_seconds(_from=2, to=4)
        self.click_button_with_text(text='Akceptuję')

    def get_next_page_arrow(self) -> WebElement:
        return self._find_element(By.XPATH, "//button[@data-cy='pagination.next-page']")

    def get_offer_urls(self, already_scraped_urls: List[str]) -> Union[List[str], bool]:
        offers = self.driver.find_elements(By.XPATH, "//a[@class='css-cl00hf e1o4jl73']")
        if not self.check_if_offers_loaded_properly(offers):
            return False

        offer_urls = [offer.get_property('href') for offer in offers
                      if offer.get_property('href') not in already_scraped_urls]

        return offer_urls

    def extract_data_from_offer(self, offer_url: str) -> None:
        if 'otodom' in offer_url:
            extractor = DataExtractorOTODOM(self.driver, self.scraped_records, page_to_extract_url=offer_url)
        else:
            raise ValueError(f"Unknown domain for data extraction: {offer_url}")

        self.scraped_records = extractor.extract()
