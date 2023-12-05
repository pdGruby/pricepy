from typing import List
from abc import ABC, abstractmethod

from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from _common.database_communicator.db_connector import DBConnector
from _common.database_communicator.tables import DataStaging, DataStagingCols, DataMain
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

        self.main_scraped_urls = None
        self.seen_records_from_db = {column.key: [] for column in DataStaging.__table__.columns}
        self.scraped_records = {column.key: [] for column in DataStaging.__table__.columns}
        self.refresh_tries = 1

    def scrape(self) -> None:
        already_scraped_urls = self.get_already_scraped_urls()

        for start_page in self.START_PAGES:
            self.enter_start_page(url=start_page)
            print(f"Successfully entered the start page: {start_page}")

            page_counter = 1
            while True:
                self.scroll_to_the_bottom()
                next_page_arrow = self.get_next_page_arrow()
                offer_urls = self.get_offer_urls(already_scraped_urls)

                #  If the page was not loaded correctly, then wait random seconds & try again collecting offers URL
                if offer_urls is False and not isinstance(offer_urls, list):
                    continue

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
                    self.save_and_clear_scraped_records()
                    print("Successfully ran through all the offers from all pages for a given start page!")
                    break

    def save_and_clear_scraped_records(self) -> None:
        sql_engine = self.create_sql_engine()

        new_records = pd.DataFrame(self.scraped_records)
        new_records.to_sql(DataStaging.__tablename__, con=sql_engine, if_exists='append', index=False)

        # Add the records that are already in the database as rows with only URLs. Thanks to that, the data cleaner will
        # update the 'last_seen_date' for existing records.
        hm_seen_records = len(self.seen_records_from_db[DataStagingCols.URL])
        for key in self.seen_records_from_db.keys():
            if key == DataStagingCols.URL:
                continue
            self.seen_records_from_db[key] += [None] * hm_seen_records

        seen_records = pd.DataFrame(self.seen_records_from_db)
        seen_records.to_sql(DataStaging.__tablename__, con=sql_engine, if_exists='append', index=False)

        for key in self.scraped_records.keys():
            self.scraped_records[key].clear()

        for key in self.seen_records_from_db.keys():
            self.scraped_records[key].clear()

    def check_if_save_threshold_reached(self) -> None:
        if len(self.scraped_records['url']) == self.DB_SAVE_THRESHOLD:
            print(f"Scraped {self.DB_SAVE_THRESHOLD} offers & matched the database save threshold. "
                  f"Saving the data into the database and proceeding...")
            self.save_and_clear_scraped_records()

    def get_already_scraped_urls(self) -> List[str]:
        cut_date = datetime.today() - relativedelta(weeks=4)

        session = self.create_session()
        staging_scraped_urls = session.query(DataStaging.url).all()
        main_scraped_urls = session.query(DataMain.url).where(DataMain.last_time_seen > cut_date).all()
        session.close()

        if not staging_scraped_urls and not main_scraped_urls:
            return []

        staging_scraped_urls = [url[0] for url in staging_scraped_urls]
        main_scraped_urls = [url[0] for url in main_scraped_urls]
        scraped_urls = staging_scraped_urls + main_scraped_urls

        self.main_scraped_urls = main_scraped_urls
        return scraped_urls

    def check_if_offers_loaded_properly(self, offer_urls) -> bool:
        if not offer_urls:
            print("Something went wrong - could not load the offers. Saved a mirror of the webpage and will try"
                  f" to refresh the page in a moment. Refresh tries: {self.refresh_tries} out of 5")

            mirror_path = f'./crawler/mirrors/{datetime.now().strftime("%Y_%m_%d___%H%M%S")}_offers_load_issue.html'
            self.save_webpage(file=mirror_path)
            self.sleep_random_seconds(_from=15, to=45)
            self.driver.refresh()
            self.refresh_tries += 1
            if self.refresh_tries > 5:
                raise TimeoutError(f"Can not load the offers. Tried {self.refresh_tries} refreshes and still no "
                                   f"results. Webpage mirrors saved to the /crawler/mirrors/ folder.")
            return False
        return True

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
