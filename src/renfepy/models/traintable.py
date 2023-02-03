from renfepy.models.train import Train
from typing import List
from rich.console import Console
from rich.table import Table
import datetime
import prettytable


class TrainTable:
    def __init__(
        self, trains: List[Train], origin: str, destination: str, date=datetime.date
    ) -> None:
        self.trains = trains
        self.origin = origin
        self.destination = destination
        self.date = date.strftime("%d/%m/%Y")

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
