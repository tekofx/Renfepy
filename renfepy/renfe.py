#!/usr/bin/python3

from selenium import webdriver
from time import sleep
import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
from rich.console import Console
from rich.table import Table
from rich.console import Console


from renfepy.logger import log
from renfepy.console import console

# Config logging
log = log.getLogger(__name__)


class Renfe_search:
    def __init__(self, gui: bool, verbose: bool):
        try:

            self.verbose = verbose

            # Setup options
            options = webdriver.ChromeOptions()
            if not gui:
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--headless")

            # Setup driver
            if not os.path.exists("/usr/bin/chromedriver"):
                log.info("Using preinstalled chromedriver")

                s = Service(
                    ChromeDriverManager().install(),
                )
            else:
                log.info("Using chromedriver from /usr/bin/chromedriver")

                s = Service(
                    executable_path="/usr/bin/chromedriver",
                )

            self.driver = webdriver.Chrome(service=s, options=options)

        except Exception as error:
            log.error("Error at setting driver: {}".format(error))
            console.print(
                "An error ocurred, check /tmp/renfe_search.log", style="bold red"
            )
            console.print("You can try to install chromium by yourself")
            sys.exit()
        else:
            html = "https://www.renfe.com/es/es"
            self.driver.get(html)
            self.wait = WebDriverWait(self.driver, 60)

    def set_origin(self, origin: str):
        """Sets the origin of the train

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
            except:
                log.error("error when selecting origin from panel")
                log.info(
                    "Selected origin {origin} from origin list".format(origin=origin)
                )

        except Exception as error:
            log.error("Error setting origin: {}".format(error))
            # self.driver.quit()

    def set_destination(self, destination: str):
        """Sets destination of the train

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

            self.driver.execute_script("arguments[0].click();", destination_list_item)
            log.info(
                "Selected destination {destination} from destination list".format(
                    destination=destination
                )
            )
        except Exception as error:
            log.error("Error at setting destination: {}".format(error))
            self.driver.quit()

    def get_selected_origin_date(self):
        # Get selected dates
        date = self.driver.find_element(By.ID, "daterange")
        selected_going_day = int(date.get_attribute("default-date-from")[8:][:-15])
        selected_going_month = int(date.get_attribute("default-date-from")[5:][:-18])
        selected_origin_year = int(date.get_attribute("default-date-from")[:-21])
        date = [selected_going_day, selected_going_month, selected_origin_year]
        return date

    def get_dates_buttons(self):
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

    def select_going_date(self, going_date):
        try:
            going_day_sum = self.get_dates_buttons()[1]
            selected_origin_date = self.get_selected_origin_date()
            going_day = going_date[0]
            going_month = going_date[1]
            going_year = going_date[2]

            selected_origin_day = selected_origin_date[0]
            selected_origin_month = selected_origin_date[1]
            selected_origin_year = selected_origin_date[2]
            while (
                selected_origin_day != going_day
                or selected_origin_month != going_month
                or selected_origin_year != going_year
            ):
                self.driver.execute_script("arguments[0].click();", going_day_sum)
                sleep(0.01)
                selected_origin_date = self.get_selected_origin_date()
                selected_origin_day = selected_origin_date[0]
                selected_origin_month = selected_origin_date[1]
                selected_origin_year = selected_origin_date[2]
        except Exception as error:
            log.error("Error selecting going date: {}".format(error))
            self.driver.quit()

    def process_date(self, date: str = None):
        """Gets a string date and transforms it into a int list

        Args:
            date (str): [description]
        """
        try:
            if date is None:
                return None
            str_date_list = date.split("-")
            output = list(map(int, str_date_list))
            return output
        except Exception as error:
            log.error("Error at processing date: {}".format(error))

    def get_difference_days(self, going_date: str, return_date):
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

    def select_return_date(self, difference_days):
        try:

            return_day_sum = self.get_dates_buttons()[3]
            for i in range(difference_days):
                self.driver.execute_script("arguments[0].click();", return_day_sum)
        except Exception as error:
            log.error("Error selecting return date: {}".format(error))
            self.driver.quit()

    def submit_search(self):
        # Introduce search
        try:
            submit_button = self.driver.find_element(
                By.CSS_SELECTOR,
                ".mdc-button.mdc-button--touch.mdc-button--unelevated.rf-button.rf-button--special.mdc-ripple-upgraded",
            )
            self.driver.execute_script("arguments[0].click();", submit_button)
            log.info("Pressed submit button")
        except Exception as error:
            log.error("Error submitting search: {}".format(error))
            self.driver.quit()

    def click_return_button(self):
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
    ):
        """Makes a search

        Args:
            origin (str): origin place
            destination (str): destination place
            going_date (str): going date
            return_date (str, optional): return date. Defaults to None.

        Returns:
            str: table with trains
        """

        # Process going date
        going_date = self.process_date(going_date)

        # Process return date
        return_date = self.process_date(return_date)

        # Set origin
        self.set_origin(origin)
        self.print("Origin set")

        # Set destination
        self.set_destination(destination)
        self.print("Destination set")

        # Select origin date
        self.select_going_date(going_date)
        self.print("Selected going date")

        aux = False
        if return_date is not None:
            difference_days = self.get_difference_days(going_date, return_date)
            self.select_return_date(difference_days)
            self.print("Selected return date")
            aux = True

        # Click search button
        self.submit_search()
        self.print("Searching")

        # Get results for going trains
        going_trains = self.get_trains()
        self.print("Getting going trains")

        if return_date != None:
            # Get results for return trains
            a = self.driver.find_elements(By.CSS_SELECTOR, ".hidden-xs.vistaPc")
            self.driver.execute_script("arguments[0].click();", a[1])
            sleep(1)
            return_trains = self.get_trains()
        else:
            return_trains = None

        self.quit_and_kill_driver()

        return going_trains, return_trains

    def print(self, txt: str, style: str = None):
        if self.verbose:
            console.print(txt, style)

    def quit_and_kill_driver(self):
        self.driver.quit()
        try:
            pid = True
            while pid:
                pid = os.waitpid(-1, os.WNOHANG)
                try:
                    if pid[0] == 0:
                        pid = False
                except:
                    pass

        except ChildProcessError:
            pass
