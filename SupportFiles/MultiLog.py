import logging
from datetime import datetime

class MultiLog:

    filePath = "AndoverAutomation\\Logs\\"

    def createLog(self,state_chosen,line_of_business,log_name):
        log = logging.getLogger(log_name)
        time_stamp = datetime.now().strftime("%m-%d-%Y - %I_%M_%S %p")
        file_formatter = logging.FileHandler(filename=f"{self.filePath}Automation_{state_chosen}_{line_of_business}_created_{time_stamp}.log") #,format='%(asctime)s - %(levelname)s - %(message)s',datefmt="%m/%d/%Y %I:%M:%S %p")
        log.setLevel(level=logging.INFO)
        log.addHandler(file_formatter)
        return log

    def add_log(self,log,message,level):
        if log is not None:
            time_stamp = datetime.now().strftime("%m-%d-%Y - %I:%M:%S %p")
            if level == logging.INFO:
                log.info(f"{time_stamp} - INFO - {message}")
            if level == logging.DEBUG:
                log.info(f"{time_stamp} - DEBUG - {message}")
            if level == logging.WARNING:
                log.info(f"{time_stamp} - WARNING - {message}")
            if level == logging.ERROR:
                log.info(f"{time_stamp} - ERROR - {message}")
            if level == logging.FATAL:
                log.info(f"{time_stamp} - FATAL - {message}")
            if level == logging.CRITICAL:
                log.info(f"{time_stamp} - CRITICAL - {message}")