import logging
from datetime import datetime

class MultiLog:
    filePath = "Logs/"
    logger = None
    log_data = False

    def createLog(self,state_chosen,line_of_business,log_name):
        log = logging.getLogger(log_name)
        time_stamp = datetime.now().strftime("%m-%d-%Y - %I_%M_%S %p")
        file_formatter = logging.FileHandler(filename=f"{MultiLog.filePath}Automation_{state_chosen}_{line_of_business}_created_{time_stamp}.log") #,format='%(asctime)s - %(levelname)s - %(message)s',datefmt="%m/%d/%Y %I:%M:%S %p")
        log.setLevel(level=logging.INFO)
        log.addHandler(file_formatter)
        self.logger = log

    def add_log(self,message,level):
        Log = self.logger
        if Log is not None and self.log_data:
            time_stamp = datetime.now().strftime("%m-%d-%Y - %I:%M:%S %p")
            if level == logging.INFO:
                Log.info(f"{time_stamp} - INFO - {message}")
            if level == logging.DEBUG:
                Log.info(f"{time_stamp} - DEBUG - {message}")
            if level == logging.WARNING:
                Log.info(f"{time_stamp} - WARNING - {message}")
            if level == logging.ERROR:
                Log.info(f"{time_stamp} - ERROR - {message}")
            if level == logging.FATAL:
                Log.info(f"{time_stamp} - FATAL - {message}")
            if level == logging.CRITICAL:
                Log.info(f"{time_stamp} - CRITICAL - {message}")
