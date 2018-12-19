'''This file contains the main interfacing
functions that are needed to access google sheets'''

import threading, time
from .my_logging import MyConsoleHandler, get_logger
logger = get_logger()

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

def sheet_upload(worksheet, content, sheet_progress):
    '''
    Upload the given content to passed Worksheet instance.

    worksheet = The worksheet object to which we are uploading data
    content = The content which we need to write in the worksheet
    sheet_progress = A 2-tuple indicating 
            * current sheet being uploaded  (int)
            * total sheets to be used       (int)
    '''

    wks = worksheet
    all_cells = wks.range(WKS_RANGE)
    sh_cur = sheet_progress[0]
    sh_total = sheet_progress[1]

    for i, part in enumerate(chunk_cell(content, CELL_CHAR_LIMIT)):

        cell = all_cells[i]
        # Add ' to prevent interpretation as formula
        cell.value = "'" + part

    total_cells_written = i + 1

    # Update the cells
    cell_chunk = 250
    for i in range(0, total_cells_written, cell_chunk):
        f = lambda : wks.update_cells(all_cells[i: i+cell_chunk])
        t = threading.Thread(target=f)
        t.daemon = True
        t.start()

        MyConsoleHandler.change_terminator('\r')
        # Change the line terminator so all subsequent lines overwrite the 
        # previous line, since we are printing a progress bar
        # Where, overwriting will give illusion of loading animation

        count = 0
        interval = 0.5 # only display every `interval` seconds
        length = 20 # length of the progress bar
        cells_done = i
        f_str = 'Sheet {:d}/{:d} | {:' + str(length) +'s} | {:d}/{:d} cells done'
        while t.is_alive():

            time.sleep(interval)

            prog_str = '#' * (count%(length+1) ) + '-' * ( length - (count%(length+1) ))
            msg = f_str.format(
                        sh_cur, sh_total, 
                        prog_str, 
                        cells_done, total_cells_written)
            logger.info(msg)

            count += 1

    
    MyConsoleHandler.restore_terminator()
    # Restoring '\n' as terminator
    # So, next .info() will end with newline
    # And subsequent calls to .info() will work normally

    # Print completed progress bar
    prog_str = '#' * length
    msg = f_str.format(
                sh_total, sh_total, 
                prog_str, 
                total_cells_written, total_cells_written)
    logger.info(msg)


def sheet_download(worksheet):
    wks = worksheet
    all_cells = wks.range(WKS_RANGE)

    return (cell.value for cell in all_cells)
