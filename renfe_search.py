#!/usr/bin/python3
from selenium import webdriver
from time import sleep
import datetime
from prettytable import PrettyTable
import logging
import sys

import selenium

# Config logging
logging.basicConfig(
    filename="/tmp/renfe_search_log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)


class Renfe_search:
    def __init__(self, gui: bool):

        self.driver = self.setup_driver(gui)
        pass

    def setup_driver(self, gui: bool):
        """Creates a selenium driver

        Returns:
            selenium.webdriver.chrome.webdriver.WebDriver: driver
        """

        try:
            options = webdriver.ChromeOptions()

            if not gui:
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--headless")
            chrome_driver_binary = "/usr/bin/chromedriver"

            # Get html
            driver = webdriver.Chrome(chrome_driver_binary, options=options)
            html = "https://www.renfe.com/es/es"
            driver.get(html)

            return driver
        except Exception as error:
            print("Error at setting driver: {}".format(error))

    def set_origin(self, origin: str):
        """Sets the origin of the train

        Args:
            origin (str): of the train
        """
        try:
            sleep(1)
            # Write the origin
            origin_text_field = self.driver.find_elements_by_id("origin")
            origin_text_field[1].send_keys(origin)
            logging.info("Written in origin search bar: {origin}".format(origin=origin))

            # Select origin from list
            origins_list = self.driver.find_elements_by_id("awesomplete_list_2_item_0")
            if len(origins_list) == 0:
                origins_list = self.driver.find_elements_by_id(
                    "awesomplete_list_1_item_0"
                )

            # FIXME: Sometimes gives error
            for x in origins_list:
                logging.info("clicked " + x.text)
            try:
                origins_list[0].click()
            except:
                logging.error("error when selecting origin from panel")
                sys.exit()
            logging.info(
                "Selected origin {origin} from origin list".format(origin=origin)
            )

        except Exception as error:
            print("Error setting origin: {}".format(error))
            # self.driver.quit()

    def set_destination(self, destination: str):
        """Sets destination of the train

        Args:
            destination (str): of the train
        """
        try:
            # Write the destination in the search box
            destination_text_field = self.driver.find_elements_by_id("destination")
            destination_text_field[1].send_keys(destination)
            logging.info(
                "Written in destination search bar: {destination}".format(
                    destination=destination
                )
            )

            # Select origing from list
            destinations_list = self.driver.find_elements_by_id(
                "awesomplete_list_1_item_0"
            )
            if (
                destination
                not in destinations_list[0].get_attribute("innerHTML").lower()
            ):
                destinations_list = self.driver.find_elements_by_id(
                    "awesomplete_list_2_item_0"
                )

            self.driver.execute_script("arguments[0].click();", destinations_list[0])
            logging.info(
                "Selected destination {destination} from destination list".format(
                    destination=destination
                )
            )
        except Exception as error:
            print("Error at setting destination: {}".format(error))
            self.driver.quit()

    def get_selected_origin_date(self):
        # Get selected dates
        date = self.driver.find_element_by_id("daterange")
        selected_going_day = int(date.get_attribute("default-date-from")[8:][:-15])
        selected_going_month = int(date.get_attribute("default-date-from")[5:][:-18])
        selected_origin_year = int(date.get_attribute("default-date-from")[:-21])
        date = [selected_going_day, selected_going_month, selected_origin_year]
        return date

    def get_dates_buttons(self):
        # Get buttons to change dates
        buttons = self.driver.find_elements_by_class_name("rf-daterange__btn")
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
            print("Error selecting going date: {}".format(error))
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
            print("Error at processing date: {}".format(error))

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
            print("Error getting difference days: {}".format(error))

    def select_return_date(self, difference_days):
        try:

            return_day_sum = self.get_dates_buttons()[3]
            for i in range(difference_days):
                self.driver.execute_script("arguments[0].click();", return_day_sum)
        except Exception as error:
            print("Error selecting return date: {}".format(error))
            self.driver.quit()

    def submit_search(self):
        # Introduce search
        try:
            submit_button = self.driver.find_element_by_css_selector(
                ".mdc-button.mdc-button--touch.mdc-button--unelevated.rf-button.rf-button--special.mdc-ripple-upgraded"
            )
            self.driver.execute_script("arguments[0].click();", submit_button)
        except Exception as error:
            print("Error submitting search: {}".format(error))
            self.driver.quit()

    def get_trains(self, type_of_train: str = None):
        output = ""
        fields = ["Train Type", "Departure", "Arrival", "Duration", "Price"]
        t = PrettyTable(fields)

        trains = self.driver.find_elements_by_class_name("trayectoRow")
        # TODO: make progress bar increment here
        for train in trains:

            # Train type
            train_type = train.find_elements_by_css_selector(".displace-text")[2].text

            # Departure
            departure = train.find_element_by_css_selector(
                ".booking-list-element-big-font.salida.displace-text-xs"
            ).text

            # Arrival
            arrival = train.find_element_by_css_selector(
                ".booking-list-element-big-font.llegada"
            ).text

            # Duration
            duration = train.find_element_by_css_selector(
                ".purple-font.displace-text.duracion.hidden-xs"
            ).text

            # Prices

            prices_list = train.find_element_by_class_name(
                "booking-list-element-price-complete"
            ).text

            if prices_list == "Tren Completo":
                prices = "Full train"

            elif "no se encuentra disponible" in prices_list:
                prices = "Train no available"

            else:
                prices = []
                for x in train.find_elements_by_css_selector(
                    ".precio.booking-list-element-big-font"
                ):
                    prices.append(x.text)

            data = [train_type, departure, arrival, duration, prices]
            if duration != "":
                if (
                    type_of_train is not None
                    and train_type.lower() == type_of_train.lower()
                ):
                    t.add_row(data)
                if type_of_train is None:
                    t.add_row(data)

        table = str(t)
        output += table
        return output

    def get_results(self, return_trains: bool, type_of_train: str = None):
        """gets a table with the trains available

        Returns:
            str: table with results
        """
        try:
            output = ""
            results = self.driver.find_element_by_id("tab-mensaje_contenido")
            message = results.get_attribute("innerHTML")
            if "no se encuentra disponible" in message:
                output += "No trains available\n"
                logging.info("Theres no trains available")

            else:
                places = self.driver.find_elements_by_css_selector("span.h3")

                # Origin
                origin = places[0].text

                # Destination
                destination = places[2].text
                output += "\n---------------Going train---------------\n"

                # Get going date
                going_date = self.driver.find_element_by_id(
                    "fechaSeleccionada0"
                ).get_attribute("value")
                # Get going trains
                output += "{place} ({date}):\n".format(place=origin, date=going_date)
                output += self.get_trains(type_of_train)

                if return_trains is True:
                    # Select return tab
                    a = self.driver.find_elements_by_css_selector(".hidden-xs.vistaPc")
                    self.driver.execute_script("arguments[0].click();", a[1])

                    # Get return date
                    return_date = self.driver.find_element_by_id(
                        "fechaSeleccionada1"
                    ).get_attribute("value")

                    output += "\n\n---------------Return train---------------\n"
                    # Check if there's return trains
                    aux = self.driver.find_element_by_id("tab-mensaje_contenido").text
                    if "no se encuentra disponible" not in aux:

                        # Get return trains
                        output += "{place} ({date}):\n".format(
                            place=destination, date=return_date
                        )
                        output += self.get_trains(type_of_train)
                    else:
                        output += "No trains available\n"
            return output
        except Exception as error:
            print("Error getting results: {}".format(error))
            return

    def make_search(
        self,
        origin: str,
        destination: str,
        going_date: str,
        return_date: str = None,
        train_type: str = None,
    ):

        # Process going date
        going_date = self.process_date(going_date)

        # Process return date
        return_date = self.process_date(return_date)

        # Set origin
        self.set_origin(origin)

        # Set destination
        self.set_destination(destination)

        # Select origin date
        self.select_going_date(going_date)

        aux = False
        if return_date is not None:
            difference_days = self.get_difference_days(going_date, return_date)
            self.select_return_date(difference_days)
            aux = True

        # Click search button
        self.submit_search()

        # Get results
        sleep(5)
        if train_type is None:
            results = self.get_results(aux)
        else:
            results = self.get_results(aux, train_type)
        self.driver.quit()

        return results


class Main:
    def print_help():
        output = """
        Usage: 
            renfe_search <origin> <destination> <going_date> [FLAGS]
            renfe_search [OPTION]

        [Flags]
            -r, --return: Set return date
            -t, --type: Set type of train
            -g, --gui: Show the browser 

        [OPTIONS]
            -h: Get help
            -i: Interactive mode
        """
        print(output)

    if len(sys.argv) == 1:
        print("Error: Not search specified")

    if sys.argv[1] == "-h":
        # Print help
        print_help()
        sys.exit()

    if sys.argv[1] == "-i":  # Interactive mode
        print("Insert origin")
        origin = input()

        print("Insert destination:")
        destination = input()

        print("Insert departure date as d-mm-yyyy")
        going_date = input()

        print("Insert return date as d-mm-yyyy or hit enter to leave it blank")
        return_date = input()
        if return_date == "":
            return_date = None

        print("Insert train type or hit enter to leave it blank")
        train_type = input()
        if train_type == "":
            train_type = None

    if "-r" in sys.argv:
        var = sys.argv.index("-r")
        return_date = sys.argv[var + 1]
    elif "--return" in sys.argv:
        var = sys.argv.index("--return")
        return_date = sys.argv[var + 1]
    else:
        return_date = None

    if "-t" in sys.argv:
        var = sys.argv.index("-t")
        train_type = sys.argv[var + 1]
    elif "-type" in sys.argv:
        var = sys.argv.index("-t")
        train_type = sys.argv[var + 1]
    else:
        train_type = None

    origin = sys.argv[1]
    destination = sys.argv[2]
    going_date = sys.argv[3]

    print("Making search...")

    if "--gui" in sys.argv or "-g" in sys.argv:
        rf = Renfe_search(True)
    else:
        rf = Renfe_search(False)

    output = rf.make_search(
        origin,
        destination,
        going_date,
        return_date,
        train_type,
    )

    print(output)


if len(sys.argv) > 1:
    m = Main()
