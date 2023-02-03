#!/usr/bin/python3
from dateutil.parser import parse
import time
from types import NoneType
from typing import Tuple
from selenium import webdriver
from time import sleep
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
from rich.console import Console
from rich.table import Table
from rich.console import Console
from logger import log
from console import console
from models.train import Train
from models.traintable import TrainTable

# Config logging
log = log.getLogger(__name__)
click = "arguments[0].click();"


class RenfePy:
    def __init__(self, gui: bool = False, verbose: bool = False):
        try:

            self.verbose = verbose

            # Setup options
            options = webdriver.FirefoxOptions()
            if not gui:
                options.add_argument("--headless")

            self.driver = webdriver.Firefox(options=options)

        except Exception as error:
            print("Error at setting driver: {}".format(error))

            sys.exit()
        else:
            html = "https://www.renfe.com/es/es"
            self.driver.get(html)

    def set_origin(self, origin: str) -> None:
        """Writes in the origin search box

        Args:
            origin (str): of the train
        """
        try:
            # Write the origin
            origin_text_field = self.driver.find_elements(By.ID, "origin")
            origin_text_field[1].send_keys(origin)
            log.info("Written in origin search bar: {origin}".format(origin=origin))

            # Select origin from list
            origins_list = self.driver.find_elements(By.ID, "awesomplete_list_2_item_0")
            if len(origins_list) == 0:
                origins_list = self.driver.find_elements(
                    By.ID, "awesomplete_list_1_item_0"
                )

            try:
                origins_list[0].click()
            except Exception as error:
                log.error("error when selecting origin from panel: {}".format(error))

        except Exception as error:
            log.error("Error setting origin: {}".format(error))
            # self.driver.quit()

    def set_destination(self, destination: str) -> None:
        """Writes in the destination search box

        Args:
            destination (str): of the train
        """
        try:
            # Write the destination in the search box
            destination_text_field = self.driver.find_elements(By.ID, "destination")
            destination_text_field[1].send_keys(destination)
            log.info(
                "Written in destination search bar: {destination}".format(
                    destination=destination
                )
            )

            # Select origing from list
            destination_list_item = self.driver.find_element(
                By.ID, "awesomplete_list_2_item_0"
            )

            if (
                destination.lower()
                not in destination_list_item.get_attribute("innerHTML").lower()
            ):
                destination_list_item = self.driver.find_element(
                    By.ID, "awesomplete_list_1_item_0"
                )

            self.driver.execute_script(click, destination_list_item)
            log.info(
                "Selected destination {destination} from destination list".format(
                    destination=destination
                )
            )
        except Exception as error:
            log.error("Error at setting destination: {}".format(error))
            self.driver.quit()

    def select_going_date(self, going_date: datetime.date) -> None:
        """Selects the going date

        Args:
            going_date (list): containing day, month and year of the going date
        """
        try:
            going_day_sum = self.driver.find_element(
                By.XPATH, "//button[contains(@aria-label, 'Sumar día fecha ida')]"
            )
            selected_origin_date = parse(
                self.driver.find_element(By.ID, "daterange").get_attribute(
                    "default-date-from"
                )
            ).date()

            while selected_origin_date != going_date:
                self.driver.execute_script(click, going_day_sum)
                sleep(0.01)
                selected_origin_date = parse(
                    self.driver.find_element(By.ID, "daterange").get_attribute(
                        "default-date-from"
                    )
                ).date()
        except Exception as error:
            log.error("Error selecting going date: {}".format(error))
            self.driver.quit()

    def select_return_date(self, return_date: datetime.date) -> None:
        """Selects the return date

        Args:
            return_date (list): containing day, month and year of the return date
        """
        try:
            return_day_sum = self.driver.find_element(
                By.XPATH, "//button[contains(@aria-label, 'Sumar día fecha vuelta')]"
            )
            selected_going_date = parse(
                self.driver.find_element(By.ID, "daterange").get_attribute(
                    "default-date-from"
                )
            ).date()
            difference_days = (return_date - selected_going_date).days

            for _ in range(difference_days):
                self.driver.execute_script(click, return_day_sum)
        except Exception as error:
            log.error("Error selecting return date: {}".format(error))
            self.driver.quit()

    def _get_trains(self):
        # FIXME: Only works for going trains

        # Get origin and destination
        aux = self.driver.find_element(By.XPATH, "//li[contains(@class, 'active')]")
        origin_destination = aux.find_element(
            By.XPATH, "//span[contains(@class, 'h3')]"
        ).text
        origin, destination = origin_destination.split(" a ")

        # Get trains
        train_table = self.driver.find_element(
            By.XPATH, "//tbody[@id='listaTrenesTBodyIda']"
        )

        style = train_table.get_attribute("style")
        if style == "display: none;":
            train_table = self.driver.find_element(
                By.XPATH, "//tbody[@id='listaTrenesTBodyVuelta']"
            )
        # if we are looking for the return trains

        going_trains = train_table.find_elements(By.CLASS_NAME, "trayectoRow")
        output = []
        for train in going_trains:

            departure = train.find_element(By.CLASS_NAME, "salida").text
            duration = train.find_element(By.CLASS_NAME, "duracion").text
            arrival = train.find_element(By.CLASS_NAME, "llegada").text

            divs = train.find_elements(By.TAG_NAME, "div")
            for div in divs:
                if div.get_attribute("aria-label") == "Tipo de tren":
                    train_type = div.text

            # Find buttons with prices
            prices = {"Básico": 0, "Elige": 0, "Prémium": 0}
            buttons = train.find_elements(By.CLASS_NAME, "next")
            # Add each price to the dict
            prices["Básico"] = buttons[0].text.replace("\n", " ")
            prices["Elige"] = buttons[1].text.replace("\n", " ")
            prices["Prémium"] = buttons[2].text.replace("\n", " ")

            output.append(
                Train(
                    origin,
                    destination,
                    train_type,
                    departure,
                    arrival,
                    duration,
                    prices,
                )
            )

        return output

    def search(
        self,
        origin: str,
        destination: str,
        going_date: str,
        return_date: str = None,
    ) -> Tuple[list, list]:
        """Gets information about trains on a certain date, and if provided, the info about trains for a return date

        Args:
            origin (str): origin place
            destination (str): destination place
            going_date (str): going date
            return_date (str, optional): return date. Defaults to None.

        Returns:
            Tuple[list, list]: each list contains dicts with the information of each train

        """

        elem = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.ID, "origin"))  # This is a dummy element
        )

        """   buttons = self.driver.find_elements(
            By.XPATH, "//button[contains(@aria-label, 'Restar día fecha ida')]"
        )
        for el in buttons:
            print(el.get_attribute("aria-label")) """

        # Process going date
        print(f"Going date: {going_date}")
        going_date = datetime.datetime.strptime(going_date, "%d/%m/%Y").date()
        print(f"Going date: {going_date}")

        # Process return date
        print(f"Return date: {return_date}")
        return_date = datetime.datetime.strptime(return_date, "%d/%m/%Y").date()
        print(f"Return date: {return_date}")

        # Get origin and destination elements
        inputs = self.driver.find_elements(By.CLASS_NAME, "awesomplete")
        origin_elements = inputs[0]
        destination_elements = inputs[1]

        # write origin
        origin_input = origin_elements.find_element(By.TAG_NAME, "input")
        origin_input.send_keys(origin)

        # TODO: Check if this is necessary
        # click on first option
        elem = WebDriverWait(origin_elements, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, "//ul[contains(@id, 'awesomplete_list_1')]")
            )  # This is a dummy element
        )
        origins_list = origin_elements.find_elements(By.TAG_NAME, "li")
        origins_first = origins_list[0]
        origins_first.click()

        # write destination
        destination_input = destination_elements.find_element(By.TAG_NAME, "input")
        destination_input.send_keys(destination)
        # click on first option
        destinations_list = destination_elements.find_elements(By.TAG_NAME, "li")
        destinations_first = destinations_list[0]
        destinations_first.click()

        # Set dates
        self.select_going_date(going_date)
        self.select_return_date(return_date)

        # Search button by XPATH which title contains "Buscar"
        submit_button = self.driver.find_element(
            By.XPATH, "//button[contains(@title, 'Buscar billete')]"
        )
        submit_button.click()

        # Get going Trains
        self.driver.execute_script("window.scrollTo(0, 100);")
        elem = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, "//tbody[@id='listaTrenesTBodyIda']")
            )
        )
        time.sleep(2)
        going_trains = self._get_trains()

        button_return = self.driver.find_element(
            By.XPATH, "//li[contains(@id, 'lab-trayecto1')]"
        ).click()

        return_trains = self._get_trains()

        self.driver.quit()
        return return_trains


if __name__ == "__main__":
    renfepy = RenfePy(gui=True, verbose=True)
    going_trains = renfepy.search("Madrid", "Barcelona", "10/02/2023", "15/02/2023")
    table = TrainTable(going_trains, "Madrid", "Barcelona")
    table.table()
