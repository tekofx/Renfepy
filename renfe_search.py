#!/usr/bin/python3
from selenium import webdriver
from time import sleep
import datetime
from prettytable import PrettyTable
import logging
import sys
import platform


# Config logging
logging.basicConfig(
    filename="logs",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)
logging.info("\n\n\nStarted script")


def setup_driver():
    """Creates a selenium driver

    Returns:
        selenium.webdriver.chrome.webdriver.WebDriver: driver
    """
    options = webdriver.ChromeOptions()

    if platform.machine() == "armv7l":
        # Options for raspbian
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")
        chrome_driver_binary = "/usr/bin/chromedriver"
    else:
        # Options for manjaro
        options.binary_location = "/usr/bin/chromium"
        # options.add_argument("--headless")
        chrome_driver_binary = "/usr/bin/chromedriver"

    # Get html
    driver = webdriver.Chrome(chrome_driver_binary, options=options)
    html = "https://www.renfe.com/es/es"
    driver.get(html)

    return driver


def set_origin(driver, origin: str):
    """Sets the origin of the train

    Args:
        driver (selenium.webdriver): driver
        origin (str): of the train
    """
    # Write the origin
    origin_text_field = driver.find_elements_by_id("origin")
    origin_text_field[1].send_keys(origin)
    logging.info("Written in origin search bar: {origin}".format(origin=origin))

    # Select origin from list
    origins_list = driver.find_elements_by_id("awesomplete_list_2_item_0")
    if len(origins_list) == 0:
        origins_list = driver.find_elements_by_id("awesomplete_list_1_item_0")

    # FIXME: Sometimes gives error
    for x in origins_list:
        print(x.text)
    try:
        origins_list[0].click()
    except:
        print("error")

    logging.info("Selected origin {origin} from origin list".format(origin=origin))


def set_destination(driver, destination: str):
    """Sets destination of the train

    Args:
        driver (selenium.webdriver): driver
        destination (str): of the train
    """
    # Write the destination in the search box
    destination_text_field = driver.find_elements_by_id("destination")
    destination_text_field[1].send_keys(destination)
    logging.info(
        "Written in destination search bar: {destination}".format(
            destination=destination
        )
    )

    # Select origing from list
    destinations_list = driver.find_elements_by_id("awesomplete_list_1_item_0")
    if destination not in destinations_list[0].get_attribute("innerHTML").lower():
        destinations_list = driver.find_elements_by_id("awesomplete_list_2_item_0")

    driver.execute_script("arguments[0].click();", destinations_list[0])
    logging.info(
        "Selected destination {destination} from destination list".format(
            destination=destination
        )
    )


def get_selected_origin_date(driver):
    # Get selected dates
    date = driver.find_element_by_id("daterange")
    selected_going_day = int(date.get_attribute("default-date-from")[8:][:-15])
    selected_going_month = int(date.get_attribute("default-date-from")[5:][:-18])
    selected_origin_year = int(date.get_attribute("default-date-from")[:-21])
    date = [selected_going_day, selected_going_month, selected_origin_year]
    return date


def get_dates_buttons(driver):
    # Get buttons to change dates
    buttons = driver.find_elements_by_class_name("rf-daterange__btn")
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


def select_origin_date(driver, going_date):
    going_day_sum = get_dates_buttons(driver)[1]
    selected_origin_date = get_selected_origin_date(driver)
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
        driver.execute_script("arguments[0].click();", going_day_sum)
        sleep(0.01)
        selected_origin_date = get_selected_origin_date(driver)
        selected_origin_day = selected_origin_date[0]
        selected_origin_month = selected_origin_date[1]
        selected_origin_year = selected_origin_date[2]


def process_date(date: str = None):
    """Gets a string date and transforms it into a int list

    Args:
        date (str): [description]
    """
    if date is None:
        return None
    str_date_list = date.split("-")
    output = list(map(int, str_date_list))
    return output


def get_difference_days(going_date: str, return_date):
    going_day = going_date[0]
    going_month = going_date[1]
    going_year = going_date[2]

    return_day = return_date[0]
    return_month = return_date[1]
    return_year = return_date[2]

    going_date = datetime.datetime(going_year, going_month, going_day)
    return_date = datetime.datetime(return_year, return_month, return_day)
    difference_days = (return_date - going_date).days
    return difference_days


def select_destination_date(driver, difference_days):
    return_day_sum = get_dates_buttons(driver)[3]
    for i in range(difference_days):
        driver.execute_script("arguments[0].click();", return_day_sum)


def submit_search(driver):
    # Introduce search
    submit_button = driver.find_elements_by_class_name("mdc-button__ripple")
    driver.execute_script("arguments[0].click();", submit_button[1])


def get_trains(driver, type_of_train: str = None):
    output = ""
    fields = ["Train Type", "Departure", "Arrival", "Duration", "Price"]
    t = PrettyTable(fields)

    trains = driver.find_elements_by_class_name("trayectoRow")
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


def get_results(driver, return_trains: bool, type_of_train: str = None):
    """gets a table with the trains available

    Returns:
        str: table with results
    """
    output = ""
    results = driver.find_element_by_id("tab-mensaje_contenido")
    message = results.get_attribute("innerHTML")
    if "no se encuentra disponible" in message:
        output += "Theres no trains available\n"
        logging.info("Theres no trains available")

    else:
        places = driver.find_elements_by_css_selector("span.h3")

        # Origin
        origin = places[0].text

        # Destination
        destination = places[2].text

        # Get going date
        going_date = driver.find_element_by_id("fechaSeleccionada0").get_attribute(
            "value"
        )
        # Get going trains
        output = "{place} ({date}):\n".format(place=origin, date=going_date)
        output += get_trains(driver, type_of_train)

        if return_trains is True:
            # Select return tab
            a = driver.find_elements_by_css_selector(".hidden-xs.vistaPc")
            driver.execute_script("arguments[0].click();", a[1])

            # Get return date
            return_date = driver.find_element_by_id("fechaSeleccionada1").get_attribute(
                "value"
            )
            # Get return trains
            output += "\n\n{place} ({date}):\n".format(
                place=destination, date=return_date
            )
            output += get_trains(driver, type_of_train)

    return output


def make_search(
    origin: str,
    destination: str,
    going_date: str,
    return_date: str = None,
    train_type: str = None,
):
    # Setup driver
    driver = setup_driver()

    # Process going date
    going_date = process_date(going_date)

    # Process return date
    return_date = process_date(return_date)

    # Set origin
    set_origin(driver, origin)

    # Set destination
    set_destination(driver, destination)

    # Select origin date
    select_origin_date(driver, going_date)

    aux = False
    if return_date is not None:
        difference_days = get_difference_days(going_date, return_date)
        select_destination_date(driver, difference_days)
        aux = True

    # Click search button
    submit_search(driver)

    # Get results
    sleep(2)
    if train_type is None:
        results = get_results(driver, aux)
    else:
        results = get_results(driver, aux, train_type)
    driver.quit()
    return results


def print_help():
    output = """
    Usage: renfe_search [FLAGS] <origin> <destination> <going_date> <return_date>

    -h: Get help
    -i: Interactive mode
    """
    print(output)


def main():
    if len(sys.argv) == 1:
        print("Error: Not search specified")

    elif sys.argv[1] == "-h":
        # Print help
        print_help()
        return

    elif sys.argv[1] == "-i":  # Interactive mode
        print("Insert origin")
        origin = input()

        print("Insert destination:")
        destination = input()

        print("Insert departure date as d-mm-yyyy")
        going_date = input()

        print("Insert return date as d-mm-yyyy")
        return_date = input()

        print("Insert train type")
        train_type = input()

    output = make_search(origin, destination, going_date, return_date, train_type)

    print(output)


if len(sys.argv) > 1:
    main()
