import logging
from logging.handlers import RotatingFileHandler

class logg:
    
    def __init__(self):
        # Log file name
        logfile = 'Q:\PlayGround\clipPy\log\Video.log'

        # Format to be used for logging
        formatter = logging.Formatter("[%(asctime)-8s] %(levelname)-8s : %(message)s")

        self.log = logging.getLogger()

        # Set the lowest logging level to be loged
        self.log.setLevel(logging.INFO)

        # Using Stream handler to print the logs on screen
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        # Log roration after 20MB total log file will be 5
        exp_file_handler = RotatingFileHandler(logfile, maxBytes=2000000, backupCount=5)
        exp_file_handler.setLevel(logging.INFO)
        exp_file_handler.setFormatter(formatter)

        # Adding both the handlers
        self.log.addHandler(console_handler)
        self.log.addHandler(exp_file_handler)