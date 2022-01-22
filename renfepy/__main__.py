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

        # Set return date
        if "-r" in sys.argv:
            index = sys.argv.index("-r")
            return_date = sys.argv[index + 1]
            log.info("Return Date: {}".format(return_date))
        elif "--return" in sys.argv:
            index = sys.argv.index("--return")
            return_date = sys.argv[index + 1]
        else:
            return_date = None

        # Set train type
        if "-t" in sys.argv:
            index = sys.argv.index("-t")
            train_type = sys.argv[index + 1]
        elif "--type" in sys.argv:
            index = sys.argv.index("--type")
            train_type = sys.argv[index + 1]
        else:
            train_type = None

        origin = sys.argv[1]
        destination = sys.argv[2]
        going_date = sys.argv[3]
        rf = Renfe_search(gui)
        search = rf.make_search(
            origin, destination, going_date, return_date, train_type
        )
        print(search)


if __name__ == "__main__":
    main()
