from typing import List

import random
import re
import os
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver


class WebdriverCreator:
    check_api_key: str = os.getenv("CRAWLER_CHECK_API_KEY")
    proxy_pool: List[str] = ["154.16.61.246:2000"]
    user_agent_pool: List[str] = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.99 Safari/537.36',  # noqa
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',  # noqa
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.99 Safari/537.36 Edg/99.0.999.99',  # noqa
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',  # noqa
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:99.0) Gecko/20100101 Firefox/99.0',  # noqa
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.99 Safari/537.36'  # noqa
    ]

    selected_proxy: str = None
    selected_user_agent: str = None
    driver: WebDriver = None

    def __init__(self):
        load_dotenv()

        self.create_driver()
        self.check_driver_options()

    def create_driver(self):
        proxy_address = random.choice(self.proxy_pool)
        user_agent = random.choice(self.user_agent_pool)

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f'--proxy-server={proxy_address}')
        chrome_options.add_argument(f"user-agent={user_agent}")
        # chrome_options.add_argument("headless")

        driver = webdriver.Chrome(options=chrome_options)

        self.selected_proxy = proxy_address
        self.selected_user_agent = user_agent
        self.driver = driver

        print(f"Chromium driver created!\nSelected proxy: {proxy_address}\nSelected user-agent: {user_agent}")

    def check_driver_options(self):
        visible_ip_address_request = f'https://api.whatismyip.com/ip.php?key={self.check_api_key}&output=json'
        visible_user_agent_request = f'https://api.whatismyip.com/user-agent.php?key={self.check_api_key}&output=json'

        self.driver.get(visible_ip_address_request)
        ip_address = re.search('"([0-9.]+)"', self.driver.page_source)

        self.driver.get(visible_user_agent_request)
        user_agent = re.search('"result":"(.*)"', self.driver.page_source)

        if ip_address is None or user_agent is None:
            raise ValueError("Could not verify visible IP Address/user-agent:"
                             f"IP Address regex: {ip_address}\nuser-agent regex: {user_agent}")

        if ip_address.group(1) != self.selected_proxy.split(':')[0]:
            raise ValueError(f"A visible IP Address is different to the selected proxy address!\n"
                             f"Selected proxy IP Address: {self.selected_proxy}\n"
                             f"Visible IP Address: {ip_address.group(1)}")

        if user_agent.group(1) != self.selected_user_agent:
            raise ValueError(f"A visible user-agent is different to the selected user agent!\n"
                             f"Selected user-agent: {self.selected_user_agent}\n"
                             f"Visible user-agent: {user_agent.group(1)}")

        print("Visible IP address & user-agent checked - all good!")
