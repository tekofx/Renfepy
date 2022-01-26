from renfepy.renfe import Renfe_search
import sys
from renfepy.logger import log
from renfepy.console import console

# Config logging
log = log.getLogger(__name__)


class main:
    def __init__(self):

        log.info("Command: {}".format(" ".join(sys.argv)))

        if "-h" in sys.argv or "--help" in sys.argv:
            console.print(self.help())
            return

        if len(sys.argv) < 4:
            console.print("Error: Data missing", style="bold red")
            log.error("Not enough data")

        else:
            with console.status("[bold green] Searching trains...") as status:
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

                # Set verbose
                if "-v" in sys.argv:
                    verbose = True
                elif "--verbose" in sys.argv:
                    verbose = True
                else:
                    verbose = False

                origin = sys.argv[1]
                destination = sys.argv[2]
                going_date = sys.argv[3]
                rf = Renfe_search(gui, verbose)
                going_trains, return_trains = rf.make_search(
                    origin, destination, going_date, return_date
                )
                rf.print_trains_table(going_trains)
                rf.print_trains_table(return_trains)

    def help(self):
        var = """
        Usage:
            renfepy  ORIGIN DESTINATION GOING_DATE [PARAMETERS]

        Example:
            renfepy  Madrid  Barcelona  30-1-2022
        
        Parameters:
            -h, --help: Show this help
            -g, --gui: Show GUI
            -v, --verbose: Show verbose
            -r, --return: Set return date"""

        return var


if __name__ == "__main__":
    main()
