import datetime
from typing import List
from typing import List
from rich.console import Console
from rich.table import Table
import datetime
import prettytable


class Train:
    def __init__(
        self,
        origin: str,
        destination: str,
        train_type: str,
        departure: datetime.datetime,
        arrival: datetime.datetime,
        duration: datetime.time,
        prices: dict,
    ) -> None:
        self.origin = origin
        self.destination = destination
        self.train_type = train_type
        self.departure = departure
        self.arrival = arrival
        self.duration = duration
        self.prices = prices

    def __str__(self) -> str:
        return f"Train from {self.origin} to {self.destination} of type {self.train_type} departing at {self.departure} and arriving at {self.arrival} with a duration of {self.duration} and prices {self.prices}"


class TrainTable:
    def __init__(
        self, trains: List[Train], origin: str, destination: str, date=datetime.date
    ) -> None:
        self.trains = trains
        self.origin = origin
        self.destination = destination
        self.date = date.strftime("%d/%m/%Y")

    def pretty_table(self) -> str:
        """Returns a pretty table with all the trains"""
        table = prettytable.PrettyTable()
        table.field_names = [
            "Tipo",
            "Salida",
            "Llegada",
            "Duración",
            "Basico",
            "Elige",
            "Premium",
        ]

        for x in self.trains:
            table.add_row(
                x.train_type,
                x.departure,
                x.arrival,
                x.duration,
                x.prices["Básico"],
                x.prices["Elige"],
                x.prices["Prémium"],
            )

        return table.get_string()

    def print_table(self) -> None:
        """Prints a table with all the trains"""
        console = Console()

        if len(self.trains) == 0:
            return console.print(
                "No hay trenes disponibles para esta ruta", style="red"
            )

        table = Table(
            title=f" {self.origin} a {self.destination} el {self.date}",
            show_lines=True,
        )
        table.add_column("Tipo")
        table.add_column("Salida")
        table.add_column("Llegada")
        table.add_column("Duración")
        table.add_column("Basico", style="yellow")
        table.add_column("Elige", style="magenta")
        table.add_column("Premium", style="red")

        for x in self.trains:
            table.add_row(
                x.train_type,
                x.departure,
                x.arrival,
                x.duration,
                x.prices["Básico"],
                x.prices["Elige"],
                x.prices["Prémium"],
            )

        console.print(table)
