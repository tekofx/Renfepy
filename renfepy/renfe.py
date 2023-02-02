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
            sleep(1)
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

    def get_selected_origin_date(self) -> list:
        """Gets the selected origin date

        Returns:
            list: containing day, month and year of the origin date
        """
        # Get selected dates
        date = self.driver.find_element(By.ID, "daterange").get_attribute(
            "default-date-from"
        )
        test = parse(date)
        print(test.day)
        selected_going_day = int(date[8:][:-15])
        selected_going_month = int(date[5:][:-18])
        selected_origin_year = int(date[:-21])
        date = [selected_going_day, selected_going_month, selected_origin_year]
        return date

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

    def get_difference_days(self, going_date: list, return_date: list) -> int:
        """Calculates the difference between the going and return date

        Args:
            going_date (list): containing day, month and year of the going date
            return_date (list): containing day, month and year of the return date

        Returns:
            int: days of difference between the going and return date
        """
        try:
            going_day = int(going_date[0])
            going_month = int(going_date[1])
            going_year = int(going_date[2])

            return_day = int(return_date[0])
            return_month = int(return_date[1])
            return_year = int(return_date[2])

            going_date = datetime.date(going_year, going_month, going_day)
            return_date = datetime.date(return_year, return_month, return_day)
            difference_days = (return_date - going_date).days
            return difference_days
        except Exception as error:
            log.error("Error getting difference days: {}".format(error))

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

    def submit_search(self) -> None:
        """Click on the submit button to search"""
        # Introduce search
        try:
            submit_button = self.driver.find_element(
                By.CSS_SELECTOR,
                ".mdc-button.mdc-button--touch.mdc-button--unelevated.rf-button.rf-button--special.mdc-ripple-upgraded",
            )
            self.driver.execute_script(click, submit_button)
            log.info("Pressed submit button")
        except Exception as error:
            log.error("Error submitting search: {}".format(error))
            self.driver.quit()

    def click_return_button(self) -> None:
        """Click on the return trains button"""
        self.driver.find_element(By.CSS_SELECTOR, ".li-trayecto").click()

    def get_trains(self) -> list:
        """Gets a list of trains

        Returns:
            list: contains dicts with the information of each train
        """
        self.driver.execute_script("window.scrollTo(0, 100);")
        self.wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "trayectoRow"))
        )

        output = []
        aux = {}
        trains = self.driver.find_elements(By.CLASS_NAME, "trayectoRow")

        for train in trains:

            # Train type
            train_type = train.find_elements(By.CSS_SELECTOR, ".displace-text")[2].text
            log.info("Train type: {}".format(train_type))

            # Departure
            departure = train.find_element(
                By.CSS_SELECTOR,
                ".booking-list-element-big-font.salida.displace-text-xs",
            ).text
            log.info("Departure: {}".format(departure))

            if not departure:
                continue

            # Arrival
            arrival = train.find_element(
                By.CSS_SELECTOR, ".booking-list-element-big-font.llegada"
            ).text
            log.info("Arrival: {}".format(arrival))

            # Duration
            duration = train.find_element(
                By.CSS_SELECTOR, ".purple-font.displace-text.duracion.hidden-xs"
            ).text
            log.info("Duration: {}".format(duration))

            # Prices
            prices_list = train.find_elements(
                By.CSS_SELECTOR, ".precio.booking-list-element-big-font"
            )
            prices = []
            for x in prices_list:
                prices.append(x.text)

            if prices == []:
                prices = "Not available"
            log.info("Prices: {}".format(prices_list))

            aux = {
                "train_type": train_type,
                "departure": departure,
                "arrival": arrival,
                "duration": duration,
                "prices": str(prices),
            }
            log.info("Train: {}".format(aux))
            output.append(aux)

        return output

    def print_trains_table(self, trains: list):
        """Prints a table with the information of each train

        Args:
            trains (list): containing dicts with the information of each train
        """
        if trains is None:
            return
        table = Table(title="Trains")

        table.add_column("Departure", justify="center", no_wrap=True)
        table.add_column("Arrival", justify="center")
        table.add_column("Duration", justify="center")
        table.add_column(
            "Price",
            justify="center",
        )
        table.add_column("Train type", justify="center")

        for train in trains:
            if train["prices"] == "Not available":
                style = "red"
            else:
                style = None

            table.add_row(
                train["departure"],
                train["arrival"],
                train["duration"],
                train["prices"],
                train["train_type"],
                style=style,
            )

        console = Console()
        console.print(table)

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

        time.sleep(5)

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

        self.select_going_date(going_date)
        self.select_return_date(return_date)
        """ time.sleep(5)

        buttons = self.driver.find_elements(By.TAG_NAME, "button")

        for button in buttons:
            print(button.text)

        submit_button = self.driver.find_element(
            By.XPATH, "//button[contains(text(), 'Buscar')]"
        )
        submit_button.click() """

        time.sleep(15)

        self.driver.quit()
        return

        # Set origin
        self.set_origin(origin)
        self.print("Origin set")

        # Set destination
        self.set_destination(destination)
        self.print("Destination set")

        # Select origin date
        self.select_going_date(going_date)
        self.print("Selected going date")

        if return_date is not None:
            difference_days = self.get_difference_days(going_date, return_date)
            self.select_return_date(difference_days)
            self.print("Selected return date")

        # Click search button
        self.submit_search()
        self.print("Searching")

        time.sleep(5)

        # Get results for going trains
        going_trains = self.get_trains()
        self.print("Getting going trains")

        if return_date != None:
            # Get results for return trains
            a = self.driver.find_elements(By.CSS_SELECTOR, ".hidden-xs.vistaPc")
            self.driver.execute_script(click, a[1])
            sleep(1)
            return_trains = self.get_trains()
        else:
            return_trains = None

        self.quit_and_kill_driver()

        return going_trains, return_trains

    def print(self, txt: str, style: str = None):
        """Prints a text with a style

        Args:
            txt (str): text to print
            style (str, optional):  styel to use. Defaults to None.
        """
        if self.verbose:
            console.print(txt, style)

    def quit_and_kill_driver(self):
        """Kills the driver"""
        self.driver.quit()


if __name__ == "__main__":
    renfepy = RenfePy(gui=True, verbose=True)
    renfepy.make_search("Madrid", "Barcelona", "10/02/2023", "15/02/2023")
