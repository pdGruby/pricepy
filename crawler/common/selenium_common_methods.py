from typing import Union, List

import random
import time

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


class SeleniumCommonMethods:
    driver: WebDriver

    def _find_element(self, by: By, expression: str, raise_exception: bool = False) -> Union[WebElement, None]:
        """
        A kind of wrapper for the 'find_element' method for Selenium elements. It allows to specify whether raise an
        exception in case of non-existence of an element or return None value.

        :param by: an attribute by which an element will be searched.
        :param expression: an expression that is used to match proper element.
        :param raise_exception: whether to raise an exception in case of non-existence of an element.
        :return:
        """
        try:
            element = self.driver.find_element(by, expression)
        except NoSuchElementException as e:
            if raise_exception:
                raise Exception(e)

            element = None

        return element

    @staticmethod
    def extract_text_from_elements(elements: List[WebElement]) -> List[str]:
        extracted_text = [element.text if element is not None else None for element in elements]
        return extracted_text

    def scroll_to_the_bottom(self) -> None:
        last_height = -999
        while True:
            scroll_by = random.randint(320, 800)

            self.driver.execute_script(f"window.scrollBy(0, {scroll_by});")
            current_height = self.driver.execute_script("return window.pageYOffset;")
            if current_height == last_height:
                break

            self.sleep_random_seconds(_from=0.1, to=0.3)
            last_height = current_height

    def scroll_until(self, element: WebElement) -> None:
        y = element.location['y']
        height = element.size['height']
        current_height = self.driver.execute_script("return window.pageYOffset;")

        if current_height > y:
            direction = '-'
        else:
            direction = ''

        hm_scrolls = 10
        diff = abs(current_height - y)
        scroll_by = diff / hm_scrolls

        for _ in range(hm_scrolls):
            self.driver.execute_script(f"window.scrollBy(0, {direction}{scroll_by});")
        self.driver.execute_script(f"window.scrollBy(0, {direction}{height*5});")

    def click_button_with_text(self, text: str) -> None:
        try:
            button = self.driver.find_element(By.XPATH, f"//*[text()='{text}']")
        except NoSuchElementException:
            pass
        else:
            button.click()

    def open_new_tab(self) -> None:
        self.driver.execute_script("window.open('about:blank', '_blank');")
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def close_active_tab(self) -> None:
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    @staticmethod
    def sleep_random_seconds(_from: float = 2, to: float = 10) -> None:
        time.sleep(random.uniform(_from, to))
