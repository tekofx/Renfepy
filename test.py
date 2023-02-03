from renfepy.renfe import RenfePy

renfepy = RenfePy(gui=False)
going_trains = renfepy.search("Madrid", "Barcelona", "04/02/2023")
going_trains.table()
