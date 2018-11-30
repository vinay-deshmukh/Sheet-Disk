'''This file contains the main interfacing
functions that are needed to access google sheets'''

# Chars allowed in each cell
# MAX STORAGE
# CELL_CHAR_LIMIT = 50000 - 1 # -1 for padding char
CELL_CHAR_LIMIT = 49500

# Cells allowed per sheet
CELLS_PER_SHEET = 1000 # A1:A1000

# Range string for worksheet
WKS_RANGE = 'A1:A1000'

# Characters allowed in one sheet
CHAR_PER_SHEET = CELL_CHAR_LIMIT * CELLS_PER_SHEET


def chunk_cell(string, cell_size):
    return (string[i:i+cell_size]
            for i in range(0, len(string), cell_size))

def sheet_upload(worksheet, content):
    wks = worksheet
    all_cells = wks.range(WKS_RANGE)

    for i, part in enumerate(chunk_cell(content, CELL_CHAR_LIMIT)):

        cell = all_cells[i]
        # Add ' to prevent interpretation as formula
        cell.value = "'" + part

    total_cells_written = i + 1

    # Update the cells
    cell_chunk = 100
    for i in range(0, total_cells_written, cell_chunk):
        wks.update_cells(all_cells[i: i+cell_chunk])


def sheet_download(worksheet):
    wks = worksheet
    all_cells = wks.range(WKS_RANGE)

    return (cell.value for cell in all_cells)

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