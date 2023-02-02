import datetime
from typing import List


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
