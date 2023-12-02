from typing import Dict

from selenium.webdriver.common.by import By

from _common.database_communicator.tables import DataStagingCols
from crawler.data_extractors.extractor_base import ExtractorBase


class DataExtractorOLX(ExtractorBase):

    def extract(self) -> Dict[DataStagingCols, str]:
        price = self._find_element(By.XPATH, '//h3')
        location = self._find_element(By.XPATH, "//div[@class='css-13l8eec']")
        desc = self._find_element(By.XPATH, "//div[@class='css-1t507yq er34gjf0']")
        image_url = self._find_element(By.XPATH, "//img")
        if image_url:
            image_url = image_url.get_attribute('src')

        data_box = self._find_element(By.XPATH, "//ul[@class='css-sfcl1s']")
        regexes_for_reading_data_box = {
            DataStagingCols.FLOOR: 'poziom: (.*)\n',
            DataStagingCols.STATUS: 'rynek: (.*)\n',
            DataStagingCols.PROPERTY_TYPE: 'rodzaj zabudowy: (.*)\n',
            DataStagingCols.SIZE: 'powierzchnia: ([0-9]+)',
            DataStagingCols.ROOMS: 'liczba pokoi: ([0-9]+)'
        }

        price, location, desc = self.extract_text_from_elements([price, location, desc])
        self.read_data_box(regexes_for_reading_data_box, data_box)
        self.scraped_records[DataStagingCols.URL].append(self.page_to_extract_url)
        self.scraped_records[DataStagingCols.PRICE].append(price)
        self.scraped_records[DataStagingCols.LOCATION].append(location)
        self.scraped_records[DataStagingCols.DESC].append(desc)
        self.scraped_records[DataStagingCols.YEAR_BUILT].append(None)
        self.scraped_records[DataStagingCols.PROPERTY_CONDITION].append(None)
        self.scraped_records[DataStagingCols.IMAGE_URL].append(image_url)

        return self.scraped_records
