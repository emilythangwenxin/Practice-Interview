# main.py
from gui.main_dashboard import launch
# TODO: Import the new admin utilities.
from app.admin_utils import init_logger, backup_data

if __name__ == "__main__":
    # TODO: Initialize the logger as the very first step.
    init_logger()

    # TODO: Perform a data backup before starting the application session.
    backup_data()

    # TODO: Launch the GUI as before.
    launch()