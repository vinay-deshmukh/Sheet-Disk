'''Logging utilities are stored in this file'''

import logging
import datetime, sys
        
# On module init
logger_made = False
g_logger = None

class MyConsoleHandler(logging.StreamHandler):
    # Modify this when printing progress bar
    terminator = logging.StreamHandler.terminator
    @classmethod
    def change_terminator(cls, repl):
        cls.terminator = repl
    @classmethod
    def restore_terminator(cls):
        cls.terminator = logging.StreamHandler.terminator

def get_logger():
    global g_logger, logger_made
    if not logger_made:
        # if logger is not created, then create it

        cur_time = str(datetime.datetime.now()).replace(':', '-').split('.')[0]
        # Get Y-M-S H:M:S

        # Set which log is required
        console = True
        file_log = False

        # Logging setup
        logger = logging.getLogger('Sheet-Disk')
        logger.setLevel(logging.DEBUG)

        
        if console:
            # Handlers
            c_handler = MyConsoleHandler(sys.stdout)
            c_handler.setLevel(logging.INFO)

            # Formatter
            c_format = logging.Formatter('%(message)s')
            c_handler.setFormatter(c_format)

            # Add the handler
            logger.addHandler(c_handler)
        
        if file_log:
            # Handlers
            f_handler = logging.FileHandler('RunLog ' + cur_time + '.log', mode='w')
            f_handler.setLevel(logging.DEBUG)

            # Formatter
            f_format = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
            f_handler.setFormatter(f_format)

            # Add the handler
            logger.addHandler(f_handler)


        g_logger = logger
        logger_made = True

    return g_logger