from typing import List

import random
import re
import os
from dotenv import load_dotenv
import subprocess

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service


class WebdriverCreator:
    CHECK_API_KEY: str
    PROXY_POOL: List[str] = ["154.16.50.29:2000"]
    USER_AGENT_POOL: List[str] = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.99 Safari/537.36',  # noqa
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',  # noqa
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.99 Safari/537.36 Edg/99.0.999.99',  # noqa
    ]
    RASPPI_CHROME_WEBDRIVER_PATH: str = '/usr/lib/chromium-browser/chromedriver'

    selected_proxy: str = None
    selected_user_agent: str = None
    driver: WebDriver = None

    def __init__(self):
        load_dotenv()
        self.CHECK_API_KEY = os.getenv("CRAWLER_CHECK_API_KEY")

        self.create_driver()
        # self.check_driver_options()

    def create_driver(self):
        proxy_address = random.choice(self.PROXY_POOL)
        user_agent = random.choice(self.USER_AGENT_POOL)

        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument(f'--proxy-server={proxy_address}')
        chrome_options.add_argument(f"user-agent={user_agent}")
        chrome_options.add_argument("--headless=new")

        # RASP PI OPTIONS
        # service = Service(executable_path=self.RASPPI_CHROME_WEBDRIVER_PATH)
        # driver = webdriver.Chrome(service=service, options=chrome_options)

        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1920, 1080)

        self.selected_proxy = proxy_address
        self.selected_user_agent = user_agent
        self.driver = driver

        print(f"Chromium driver created!\nSelected proxy: {proxy_address}\nSelected user-agent: {user_agent}")

    def check_driver_options(self):
        visible_ip_address_request = f'https://api.whatismyip.com/ip.php?key={self.CHECK_API_KEY}&output=json'
        visible_user_agent_request = f'https://api.whatismyip.com/user-agent.php?key={self.CHECK_API_KEY}&output=json'

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

    @staticmethod
    def kill_webdriver_processes():
        """Since simple self.driver.quit() doesn't work, we kill the processes with the bash commands"""
        command_1 = 'pkill -f chromedriver'
        command_2 = 'pkill -f chromium-browse'
        result_1 = subprocess.run(command_1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        result_2 = subprocess.run(command_2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f'Chrome webdriver has been killed. Return results: {result_1}; {result_2}')
