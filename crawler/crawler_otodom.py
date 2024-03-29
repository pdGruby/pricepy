from typing import List, Union

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from _common.database_communicator.tables import DataStagingCols
from crawler.crawler_base import CrawlerBase
from crawler.data_extractors.extractor_otodom import DataExtractorOTODOM


class CrawlerOTODOM(CrawlerBase):
    START_PAGES = ['https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/wielkopolskie/poznan/poznan/poznan?limit=36&' +
                   'ownerTypeSingleSelect=ALL&daysSinceCreated=7&by=DEFAULT&direction=DESC&viewType=listing',
                   'https://www.otodom.pl/pl/wyniki/sprzedaz/dom/wielkopolskie/poznan/poznan/poznan?distanceRadius=0&' +
                   'limit=36&ownerTypeSingleSelect=ALL&daysSinceCreated=7&by=DEFAULT&direction=DESC&viewType=listing']

    def __init__(self):
        super().__init__()

    def enter_start_page(self, url: str) -> None:
        self.driver.get(url)
        self.sleep_random_seconds(_from=2, to=4)
        self.click_button_with_text(text='Akceptuję')

    def get_next_page_arrow(self) -> WebElement:
        button = self._find_element(By.XPATH, "//li[@title='Go to next Page']")

        # Old OTODOM version, perhaps will be removed completely by the developers in the nearest future
        if button is None:
            print("The old OTODOM webpage has just been loaded")
            button = self._find_element(By.XPATH, "//button[@data-cy='pagination.next-page']")

            if button is None:
                print("Could not find the old next page button & the new old page button. End of available offers?")
                return None
        ###

        if button.get_attribute('disabled'):
            button = None

        return button

    def get_offer_urls(self, already_scraped_urls: List[str]) -> Union[List[str], bool]:
        offers = self.driver.find_elements(By.XPATH, "//a[@class='css-16vl3c1 e1njvixn0']")

        # Old OTODOM version, perhaps will be removed completely by the developers in the nearest future
        if not offers:
            print("The old OTODOM webpage has just been loaded")
            offers = self.driver.find_elements(By.XPATH, "//a[@data-cy='listing-item-link']")
        ###

        if not self.check_if_offers_loaded_properly(offers):
            return False

        offer_urls = []
        for offer in offers:
            href = offer.get_property('href')
            if '/inwestycja/' in href:
                continue

            if href in self.main_scraped_urls:
                self.seen_records_from_db[DataStagingCols.URL].append(href)
                continue
            if href in already_scraped_urls:
                continue

            offer_urls.append(href)

        return offer_urls

    def extract_data_from_offer(self, offer_url: str) -> None:
        if 'otodom' in offer_url:
            extractor = DataExtractorOTODOM(self.driver, self.scraped_records, page_to_extract_url=offer_url)
        else:
            raise ValueError(f"Unknown domain for data extraction: {offer_url}")

        self.scraped_records = extractor.extract()
