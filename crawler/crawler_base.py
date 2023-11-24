from typing import List
from abc import ABC, abstractmethod

import pandas as pd
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from _common.database_communicator.db_connector import DBConnector
from _common.database_communicator.tables import DataStaging
from crawler.common.selenium_common_methods import SeleniumCommonMethods
from crawler.common.webdriver_creator import WebdriverCreator


class CrawlerBase(WebdriverCreator, DBConnector, SeleniumCommonMethods, ABC):
    DB_SAVE_THRESHOLD: int = 20
    START_PAGES: List[str]
    driver: WebDriver

    def __init__(self):
        ABC.__init__(self)
        WebdriverCreator.__init__(self)
        DBConnector.__init__(self)

        self.scraped_records = {column.key: [] for column in DataStaging.__table__.columns}

    def scrape(self) -> None:
        already_scraped_urls = self.get_already_scraped_urls()

        for start_page in self.START_PAGES:
            self.enter_start_page(url=start_page)

            page_counter = 1
            while True:
                self.scroll_to_the_bottom()
                next_page_arrow = self.get_next_page_arrow()
                offer_urls = self.get_offer_urls(already_scraped_urls)

                print(f"Found {len(offer_urls)} offers to scrape on the page number {page_counter}. Extracting the "
                      f"data...")
                self.open_new_tab()

                for offer_url in offer_urls:
                    self.driver.get(offer_url)
                    self.sleep_random_seconds()
                    self.extract_data_from_offer(offer_url)
                    self.check_if_save_threshold_reached()

                self.close_active_tab()
                print(f"Successfully scraped all offers from the page number {page_counter}. Continuing...")

                if next_page_arrow:
                    self.scroll_until(element=next_page_arrow)
                    next_page_arrow.click()
                    page_counter += 1
                else:
                    print("Successfully ran through all the offers from all pages for a given init page!")
                    break

    def save_and_clear_scraped_records(self) -> None:
        sql_engine = self.create_sql_engine()

        data = pd.DataFrame(self.scraped_records)
        data.to_sql(DataStaging.__tablename__, con=sql_engine, if_exists='append', index=False)

        for key in self.scraped_records.keys():
            self.scraped_records[key].clear()

    def check_if_save_threshold_reached(self) -> None:
        if len(self.scraped_records['url']) == self.DB_SAVE_THRESHOLD:
            print(f"Scraped {self.DB_SAVE_THRESHOLD} offers & matched the database save threshold. "
                  f"Saving the data into the database and proceeding...")
            self.save_and_clear_scraped_records()

    def get_already_scraped_urls(self) -> List[str]:
        session = self.create_session()
        scraped_urls = session.query(DataStaging.url).all()
        session.close()

        if not scraped_urls:
            return []

        return [url[0] for url in scraped_urls]

    @abstractmethod
    def enter_start_page(self, url: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_next_page_arrow(self) -> WebElement:
        raise NotImplementedError

    @abstractmethod
    def get_offer_urls(self, already_scraped_urls: List[str]) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def extract_data_from_offer(self, offer_url: str) -> None:
        raise NotImplementedError