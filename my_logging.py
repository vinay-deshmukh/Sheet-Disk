'''Logging utilities are stored in this file'''

# On module init
logger_made = False
g_logger = None

def get_logger():
    global g_logger, logger_made
    if not logger_made:
        # if logger is not created, then create it

        import logging
        import datetime, sys
        cur_time = str(datetime.datetime.now()).replace(':', '-').split('.')[0]
        # Get Y-M-S H:M:S

        # Logging setup
        logger = logging.getLogger('Sheet-Disk')
        logger.setLevel(logging.DEBUG)

        # Handlers
        c_handler = logging.StreamHandler(sys.stdout)
        c_handler.setLevel(logging.INFO)
        f_handler = logging.FileHandler('RunLog ' + cur_time + '.log', mode='w')
        f_handler.setLevel(logging.DEBUG)

        # Formatter
        c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        f_format = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
        f_handler.setFormatter(f_format)

        # Add handlers to the logger
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)

        g_logger = logger
        logger_made = True

    return g_logger