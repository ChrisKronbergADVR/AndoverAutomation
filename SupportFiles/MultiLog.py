import logging
from datetime import datetime
import threading
import os


class MultiLog:
    filePath = "Logs/"
    log_data = False
    log_path = datetime.now()
    year = log_path.year
    month = log_path.month
    day = log_path.day

    day_path = f"{filePath}{year}/{month}/{day}/"

    @staticmethod
    def create_log(state_chosen, line_of_business):
        log = logging.getLogger(threading.current_thread().name)
        time_stamp = datetime.now().strftime("%m-%d-%Y - %I_%M_%S %p")
        file_formatter = logging.FileHandler(filename=f"{MultiLog.day_path}Automation_{state_chosen}_{line_of_business}_created_{
                                             time_stamp}.log")  # ,format='%(asctime)s - %(levelname)s - %(message)s',datefmt="%m/%d/%Y %I:%M:%S %p")
        log.setLevel(level=logging.INFO)
        log.addHandler(file_formatter)

    @staticmethod
    def add_log(message, level):
        Log = logging.getLogger(threading.current_thread().name)
        log_level = {logging.INFO: "INFO", logging.DEBUG: "DEBUG", logging.WARNING: "WARNING",
                     logging.ERROR: "ERROR", logging.FATAL: "FATAL", logging.CRITICAL: "CRITICAL"}
        if Log is not None and MultiLog.log_data:
            time_stamp = datetime.now().strftime("%m-%d-%Y - %I:%M:%S %p")
            Log.info(f"{time_stamp} - {log_level[level]} - {message}")
