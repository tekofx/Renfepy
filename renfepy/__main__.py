from renfepy.renfe import Renfe_search
import sys
from renfepy.logger import log


class main:

    # Config logging
    log = log.getLogger(__name__)

    log.info("Command: {}".format(" ".join(sys.argv)))

    if len(sys.argv) < 4:
        print("Error: Data missing")
        log.error("Not enough parameters")
    else:

        if "-g" in sys.argv or "--gui" in sys.argv:
            gui = True
            log.info("GUI: True")
        else:
            gui = False
            log.info("GUI: False")

        origin = sys.argv[1]
        destination = sys.argv[2]
        going_date = sys.argv[3]
        rf = Renfe_search(gui)
        search = rf.make_search(origin, destination, going_date)
        rf.print_trains_table(search)
        print(search)


if __name__ == "__main__":
    main()
