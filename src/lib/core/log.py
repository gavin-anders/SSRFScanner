'''
Created on 4 Mar 2018

@author: gavin
'''
from lib.thirdparty.logutils.colorize import ColorizingStreamHandler
from lib.core.settings import APPLICATION, LOG_FILE_ROTATE, LOG_LEVEL, LOG_MAX_BYTES, LOG_MAX_BYTES, LOG_PATH
from logging.handlers import RotatingFileHandler
from lib.core.utils import stop_running

import logging, os

class CustomLogger(logging.Logger):
    TAMPER = 11     # used for logging the tampered parameter / value
    REQUEST = 8    # used for logging the requests
    RESPONSE = 7   # used for logging the response
    
    def __init__(self, *args, **kwargs):
        super(CustomLogger, self).__init__(*args, **kwargs)
        logging.addLevelName(CustomLogger.TAMPER, 'TAMPER')
        logging.addLevelName(CustomLogger.REQUEST, 'REQUEST')
        logging.addLevelName(CustomLogger.RESPONSE, 'RESPONSE')
        self.setLevel(logging.INFO)
        
    def exception(self, msg, *args, **kwargs):
        logging.Logger.critical(self, msg, *args, **kwargs)
        stop_running()
        
    def tamper(self, msg, *args, **kwargs):
        self.log(CustomLogger.TAMPER, msg, *args, **kwargs)
        
    def request(self, msg, *args, **kwargs):
        msg = "\n" + msg.rstrip()
        self.log(CustomLogger.REQUEST, msg, *args, **kwargs)
        
    def response(self, msg, *args, **kwargs):
        self.log(CustomLogger.RESPONSE, msg, *args, **kwargs)

class ColorHandler(ColorizingStreamHandler):
    def __init__(self, *args, **kwargs):
        super(ColorHandler, self).__init__(*args, **kwargs)
        self.level_map = {
                # Provide you custom coloring information here
                logging.DEBUG: (None, 'blue', True),
                logging.INFO: (None, 'green', True),
                logging.WARNING: (None, 'yellow', False),
                logging.ERROR: (None, 'red', False),
                logging.CRITICAL: ('red', 'white', True),
        }


logging.setLoggerClass(CustomLogger)
LOG = logging.getLogger(APPLICATION)

def setup_logging(level):
    '''
    sets up the logging handlers to stdout and file
    '''
    if level == 1:
        LOG.setLevel(logging.INFO)
    elif level == 2:
        LOG.setLevel(CustomLogger.TAMPER)
    elif level == 3:
        LOG.setLevel(logging.DEBUG)
    elif level == 4:  
        LOG.setLevel(CustomLogger.REQUEST)
    elif level == 5:  
        LOG.setLevel(CustomLogger.RESPONSE)
        
    # formatting
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%H:%M:%S")    
    
    # log to stdout
    colourhandler = ColorHandler()
    colourhandler.level_map[CustomLogger.TAMPER] = (None, "cyan", False)
    colourhandler.level_map[CustomLogger.REQUEST] = (None, "yellow", True)
    colourhandler.level_map[CustomLogger.RESPONSE] = (None, "green", False)
    colourhandler.setFormatter(formatter)
    LOG.addHandler(colourhandler)
    
    # log to file
    filehandler = RotatingFileHandler(LOG_PATH, maxBytes=LOG_MAX_BYTES, backupCount=LOG_FILE_ROTATE)
    filehandler.setFormatter(formatter)
    LOG.addHandler(filehandler)

