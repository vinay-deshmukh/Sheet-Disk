'''This file contains the main interfacing
functions that are needed to access google sheets'''

import threading, time
from queue import Queue
from .my_logging import MyConsoleHandler, get_logger
logger = get_logger()

# Chars allowed in each cell
# MAX STORAGE
# CELL_CHAR_LIMIT = 50000 - 1 # -1 for padding char
CELL_CHAR_LIMIT = 49500 # +1 for the quote character

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
    Returns total cells written in the worksheet

    worksheet = The worksheet object to which we are uploading data
    content = The content which we need to write in the worksheet
    sheet_progress = A 2-tuple indicating 
            * current sheet being uploaded  (int)
            * total sheets to be used       (int)
    '''

    wks = worksheet
    all_cells = wks.range(WKS_RANGE)
    # Very inexpensive, quick operation 
    # since wks is empty for new file

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

    return total_cells_written


def sheet_download(worksheet, sheet_progress, cell_count):
    '''
    Download content from given worksheet instance

    worksheet = The worksheet object from which we are downloading data
    instance_sheetdownload = an instance of the SheetDownload class being
        used to download the sheet
    sheet_progress = A 2-tuple indicating 
            * current sheet being uploaded  (int)
            * total sheets to be used       (int)
    '''
    wks = worksheet
    sh_cur = sheet_progress[0]
    sh_total = sheet_progress[1]

    n_threads = 10
    data_list = [None] * n_threads
    data_lock = threading.Lock()
    data_count_queue = Queue()
    # this queue is used to get the number of cells
    # completed by a thread
    # Threads will put (no of cells done) in queue
    # progress bar print will get them and increment counter

    thread_details = {
        'wks': wks,
        'data_list': data_list,
        'data_lock': data_lock,
        'data_count_queue': data_count_queue,
    }

    thread_list = []
    for t_no, start, end in work_divider(
                    no_of_cells=cell_count,
                    n_threads=n_threads
                    ):

        t = threading.Thread(
                target=worker_download,
                name='Thread ' + str(t_no),
                args=(t_no, start, end, thread_details),
                )

        logger.debug('Created thread ' + str(t_no))
        thread_list.append(t)
        t.daemon = True

    # HANDLE ALL THREADING STUFF
    thread_runner_factory(
            thread_list, 
            data_count_queue, 
            sheet_progress=(sh_cur, sh_total))
    # the threads assign data to data_list, which is
    # passed as argument to each thread
    # Each thread can access data_list using data_lock

    for row in data_list:
        if row is not None:
            for cell in row:
                yield cell.value[1:] # Remove padding char


def worker_download(thread_no, start, end, thread_details):
    wks = thread_details['wks']
    data_list = thread_details['data_list']
    data_lock = thread_details['data_lock']
    data_count_queue = thread_details['data_count_queue']

    name = threading.current_thread().name

    logger.debug(name + ': Starting download')
    t_cells = wks.range('A' + str(start) + ':A' + str(end))
    logger.debug(name + ': done download')

    with data_lock:
        data_list[thread_no] = t_cells
    logger.debug(name + ' has assigned data to data_list')

    total_cells_done = end - start + 1
    data_count_queue.put(total_cells_done)

    logger.debug(name + ' has put progress to queue')
    logger.debug(name + ' end: Returned data')

def thread_runner_factory(thread_list, data_count_queue, sheet_progress):
    '''
    Takes a list of threads, and manages their concurrency and also 
    prints appropriate progress bars.

    thread_list = List of thread objects
    data_count_queue = Queue object, 
            to which the threads put their progress as ints
    sheet_progress = A 2-tuple indicating 
            * current sheet being uploaded  (int)
            * total sheets to be used       (int)
    '''

    sh_cur = sheet_progress[0]
    sh_total = sheet_progress[1]

    for t in thread_list:
        t.start()
        logger.debug('Started thread ' + t.name)

    interval = 0.8 # sec
    counter = 1
    length = 20
    completed_cells = 0
    latest_done_cells = 0 # re init for each sheet
    
    f_str = 'Sheet {:d}/{:d} | {:' + str(length) + 's} | {:d} cells done'

    MyConsoleHandler.change_terminator('\r')

    while any( t.is_alive() for t in thread_list ) or not data_count_queue.empty():
        # While any of the threads is alive
        # ie while atleast one thread is alive
        # or
        # while queue is not empty

        prog = '#' * (counter%(length+1)) + '-' * (length - (counter%(length+1)))
        latest_done_cells = data_count_queue.get()
        data_count_queue.task_done()

        completed_cells += latest_done_cells

        msg = f_str.format(sh_cur, sh_total, prog, completed_cells)
        logger.info(msg)

        if not any( t.is_alive() for t in thread_list ):
            # if all threads are dead
            # empty the queue quickly and break out
            logger.debug('All threads are unalive so emptying the queue and breaking out')
            while not data_count_queue.empty():
                completed_cells += data_count_queue.get()
                data_count_queue.task_done()

            # Break out after queue is emptied
            break 

        counter += 1
        time.sleep(interval)


    # Print 100% message
    MyConsoleHandler.restore_terminator()
    prog = '#' * length
    msg = f_str.format(sh_cur, sh_total, prog, completed_cells)
    logger.info(msg)

    
    logger.info("All threads are aliven't!")

    for t in thread_list:
        # Making certain all threads are stopped
        t.join()
        logger.debug(t.name + ' joined')


def work_divider(no_of_cells, n_threads):
    '''Divide the no of cells almost equally among n_threads'''

    # https://math.stackexchange.com/a/1081099
    
    N = no_of_cells
    M = n_threads
    for i, k in enumerate(range(M)):
        start_index = (N * k) // M + 1
        inc = (N *(k+1))//M - start_index 
        end_index = start_index + inc
        
        # i is the thread number
        yield i, start_index, end_index