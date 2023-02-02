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

    def get_dates_buttons(self) -> list:
        """Gets the dates buttons to increase and decrease the date of the going and returning

        Returns:
            list: containing buttons decrease_going_date, increase_going_date, decrease_returning_date, increase_returning_date
        """
        # Get buttons to change dates
        buttons = self.driver.find_elements(By.CLASS_NAME, "rf-daterange__btn")
        for el in buttons:
            if "Restar día fecha ida" in el.get_attribute("aria-label"):
                going_day_rest = el
            elif "Sumar día fecha ida" in el.get_attribute("aria-label"):
                going_day_sum = el
            elif "Restar día fecha vuelta" in el.get_attribute("aria-label"):
                return_day_rest = el
            else:
                return_day_sum = el

        output = [going_day_rest, going_day_sum, return_day_rest, return_day_sum]
        return output

    def select_going_date(self, going_date: datetime.date) -> None:
        """Selects the going date

        Args:
            going_date (list): containing day, month and year of the going date
        """
        try:
            going_day_sum = self.get_dates_buttons()[1]
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
            return_day_sum = self.get_dates_buttons()[3]
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

    def make_search(
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
        # click on first option
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

        # Get Trains
        self.driver.execute_script("window.scrollTo(0, 100);")
        elem = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "next"))
        )
        trains = self.driver.find_elements(By.CLASS_NAME, "trayectoRow")

        output = []
        for train in trains:
            # Find div by XPATH which aria label is Tipo de tren
            train_type = train.find_element(
                By.XPATH, "//div[@aria-label='Tipo de tren']"
            ).text

            # Find div by XPATH which aria label is Hora de salida
            departure = train.find_element(
                By.XPATH, "//div[@aria-label='Hora de salida']"
            ).text

            # Find div by XPATH which aria label is Hora de llegada
            arrival = train.find_element(
                By.XPATH, "//div[@aria-label='Hora de llegada']"
            ).text

            # Find div by XPATH which aria label is Duración
            duration = train.find_element(
                By.XPATH, "//div[@aria-label='Duración']"
            ).text

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

        self.driver.quit()
        return output


if __name__ == "__main__":
    renfepy = RenfePy(gui=True, verbose=True)
    trains = renfepy.make_search("Madrid", "Barcelona", "10/02/2023", "15/02/2023")
    for train in trains:
        print(train)
