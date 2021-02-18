import os

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from .log import Log
import time
import sys



class FaucetCollector:
    def __init__(self):

        self.driver_path = self._configParser()[1]
        self.browser_mode = self._configParser()[0]
        self.browser_binary_location = self._configParser()[2]
        self.log = Log()
        self.driver = Chrome(options=self._get_opts(), executable_path=self.driver_path)
        self.crypto_faucets = {}

    def collect_crypto_faucets(self, crypto_faucets: str):
        self.log.write_log("Bot", f"Collecting crypto faucets...")
        with open(crypto_faucets, "r") as file:
            lines = file.readlines()
            for line in lines:
                url, user, password = line.split(";")
                self.crypto_faucets.update(
                    {url: {
                        "user": user,
                        "password": password
                    }})


    def start_collecting_crypto(self):

        for url in self.crypto_faucets:
            try:
                self.log.write_log("browser", f"Browser Open")
                self.log.write_log("Bot", f"Visiting {url}")
                self.driver.get(url)
                self.login(url=url)
                self.claim_faucet(url=url)
                self.check_balance(url=url)
            except Exception as e:
                self.log.write_log("warning", e)
                self.error_handler(e)
                break

        self.quit()

    def login(self, url: str):
        user = self.crypto_faucets[url]["user"]
        password = self.crypto_faucets[url]["password"]
        self.log.write_log("Bot", f"Logging in...")

        self.__get_xpath_elem('/html/body/main/section/section[1]/div/div/div[2]/div/div[1]/div[1]/input').send_keys(user)

        self.__get_xpath_elem('/html/body/main/section/section[1]/div/div/div[2]/div/div[1]/div[2]/input').send_keys(password)

        self._modal_advertisement_login()
        self._random_wait(1, 2)

        self._click('/html/body/main/section/section[1]/div/div/div[2]/div/div[1]/button', "CLick Login")

        WebDriverWait(self.driver,5).until(lambda driver: driver.current_url != f"{url}/")

    def claim_faucet(self, url: str):

        try:
            WebDriverWait(self.driver, 5).until(expected_conditions.element_to_be_clickable((By.XPATH, "/html/body/main/div/div/div/div/div/div[5]/button"))).click()
            success_message = (WebDriverWait(self.driver, 5).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, "result"))).text)

            self.log.write_log("success", self.log.green_text(f"Claiming crypto {url}"))

        except TimeoutException:
            minutes = self.driver.find_element_by_xpath("/html/body/main/div/div/div/div/div/div[2]/div[1]/div/div[1]/div[1]").text
            seconds = self.driver.find_element_by_xpath("/html/body/main/div/div/div/div/div/div[2]/div[1]/div/div[2]/div[1]").text
            self.log.write_log("warning", f'Error Claiming crypto {url}')
            self.log.write_log("warning", f'Wait Until {minutes} Minutes {seconds} Seconds')
            self.error_handler(f'Error Claiming crypto {url}')
            pass

    def check_balance(self, url: str):
        balance = ""

        balance = self.driver.find_element_by_xpath("/html/body/header/div/div[1]/nav/div/ul/li[11]/a").text
        self.log.write_log("success", self.log.green_text(f"Current balance: {balance} \n"))
    
        

    def _modal_advertisement_login(self):

        try:
            self._click('/html/body/div[1]/div', "Close Modal Advertisement Login")
        except Exception as e:
            pass


    def _get_opts(self):

        opts = webdriver.chrome.options.Options()

        if self.browser_mode == "headless":
            opts.add_argument("--headless")

        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.binary_location = self.browser_binary_location
        opts.add_argument("--ignore-certificate-erors")
        opts.add_argument("window-size=1920,1080")
        opts.add_argument("start-maximized")
        opts.add_argument("disable-infobars")
        opts.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)

        return opts

    def _configParser(self):

        from configparser import ConfigParser

        config = ConfigParser()
        config.readfp(open(f"config.cfg"))

        browser_mode = config.get("Browser", "browser-mode")
        driver_path = config.get("Browser", "driver-path")
        browser_binary_location = config.get("Browser", "browser-binary-location")


        return (
            browser_mode,
            driver_path,
            browser_binary_location,
        )

    def quit(self):
        self.log.write_log("browser", 'Close Browser')
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            self.driver.close()

    def sleep(self, mins):

        import time

        self.log.write_log("bot", self.log.yellow_text(f"Sleeping for {mins} sec"))
        time.sleep(int(mins))

    def error_handler(self, msg):
        self.log.error_log(msg)

    def _click(self, element, msg="placeholder"):

        self.log.write_log("bot",f"clicking on {msg}")
        self.driver.find_element_by_xpath(element).click()

    def _random_wait(self, t_min, t_max):

        import time
        import random

        random_time = random.randrange(t_min, t_max)
        # self.log.write_log("bot", f"Waiting for {random_time} sec")
        time.sleep(random_time)


    def __get_xpath_elem(self, element):

        try:
            return self.driver.find_element_by_xpath(element)
        except Exception as e:
            self.log.write_log("warning", e)
            self.error_handler(e)
            pass

