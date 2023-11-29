from typing import Dict

from selenium.webdriver.common.by import By

from _common.database_communicator.tables import DataStagingCols
from crawler.data_extractors.extractor_base import ExtractorBase


class DataExtractorOTODOM(ExtractorBase):

    def extract(self) -> Dict[DataStagingCols, str]:
        self.click_button_with_text(text='Akceptuję')  # needed when entering the otodom page from olx page
        self.click_button_with_text(text='Pokaż więcej')

        price = self._find_element(By.XPATH, "//strong")
        location = self._find_element(By.XPATH, "//a[@aria-label='Adres']")
        desc = self._find_element(By.XPATH, "//div[@class='css-1wekrze e1lbnp621']")
        image_url = self._find_element(By.XPATH, "//img[@class='image-gallery-image']")
        if image_url:
            image_url = image_url.get_attribute('src')

        upper_data_box = self._find_element(By.XPATH, "//div[@class='css-xr7ajr e10umaf20']")
        regexes_for_reading_upper_data_box = {
            DataStagingCols.FLOOR: 'piętro\\n(.*)\\n',
            DataStagingCols.SIZE: 'powierzchnia\\n([0-9]+[,]?[0-9]+)',
            DataStagingCols.ROOMS: 'liczba pokoi\\n([0-9]+)\\n',
            DataStagingCols.PROPERTY_CONDITION: 'stan wykończenia\\n(.*)\\n'
        }

        lower_data_box = self._find_element(By.XPATH, "//div[@class='css-1utkgzv e10umaf20']")
        regexes_for_reading_lower_data_box = {
            DataStagingCols.STATUS: 'rynek\\n(.*)\\n',
            DataStagingCols.YEAR_BUILT: 'rok budowy\\n(.*)\\n',
            DataStagingCols.PROPERTY_TYPE: 'rodzaj zabudowy\\n(.*)\\n'
        }

        price, location, desc = self.extract_text_from_elements([price, location, desc])
        self.read_data_box(regexes=regexes_for_reading_upper_data_box, data_box=upper_data_box)
        self.read_data_box(regexes=regexes_for_reading_lower_data_box, data_box=lower_data_box)
        self.scraped_records[DataStagingCols.URL].append(self.page_to_extract_url)
        self.scraped_records[DataStagingCols.PRICE].append(price)
        self.scraped_records[DataStagingCols.LOCATION].append(location)
        self.scraped_records[DataStagingCols.DESC].append(desc)
        self.scraped_records[DataStagingCols.IMAGE_URL].append(image_url)

        return self.scraped_records
