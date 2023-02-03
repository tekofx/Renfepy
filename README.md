<h1 align="center">Renfepy</h1>

<p align="center"><img width=50% src="./assets/logo.png"></p>
<p align="center">Python library to search for trains on renfe.es<p>

# Installation

`pip3 install renfepy`

If chromium is not installed Renfepy will install a it. In case of error it is recommended to install it.

# Usage

```py
from renfepy.renfe import RenfePy

renfepy = RenfePy(gui=False)
going_trains = renfepy.search("Madrid", "Barcelona", "04/02/2023")
going_trains.table()
```
