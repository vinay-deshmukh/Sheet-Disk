'''This file contains the main interfacing
functions that are needed to access google sheets'''

import threading, time
from queue import Queue, Empty as queueEmpty
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

# No. of threads to use
N_THREADS = 11

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

    for i, part in enumerate(chunk_cell(content, CELL_CHAR_LIMIT)):

        cell = all_cells[i]
        # Add ' to prevent interpretation as formula
        cell.value = "'" + part

    total_cells_written = i + 1

    data_count_queue = Queue()
    # this queue is used to get the number of cells
    # completed by a thread
    # Threads will put (no of cells done) in queue
    # progress bar print will get them and increment counter

    thread_details ={
        'wks': wks,
        'data_count_queue': data_count_queue,
    }

    n_threads = N_THREADS
    thread_list = []

    for t_no, start, end in work_divider(
                    no_of_cells=total_cells_written,
                    n_threads=n_threads
                    ):

        t = threading.Thread(
                target=worker_upload,
                name='Thread ' + str(t_no),
                args=(all_cells[start-1:end], thread_details)
                )
        # start-1, since start is 1-index, all_cells is 0-indexed
        t.daemon = True
        logger.debug('Created thread ' + t.name)
        thread_list.append(t)
        
    # HANDLE ALL THREADING STUFF
    thread_runner_factory(
        thread_list, 
        data_count_queue, 
        sheet_progress,
        total_cells=total_cells_written)

    return total_cells_written

def worker_upload(cell_list, thread_details):

    wks = thread_details['wks']
    data_count_queue = thread_details['data_count_queue']
    name = threading.current_thread().name

    logger.debug(name + ': Starting upload')
    wks.update_cells(cell_list)
    logger.debug(name + ': Done upload')

    total_cells_done = len(cell_list)
    data_count_queue.put(total_cells_done)
    logger.debug(name + ' has put progress to queue')

    logger.debug(name + ': end function')

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

    n_threads = N_THREADS
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
        t.daemon = True
        logger.debug('Created thread ' + t.name)
        thread_list.append(t)

    # HANDLE ALL THREADING STUFF
    thread_runner_factory(
            thread_list, 
            data_count_queue, 
            sheet_progress,
            total_cells=cell_count)
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

def thread_runner_factory(thread_list, data_count_queue, sheet_progress, total_cells):
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

    interval = 0.4 # sec
    counter = 1
    length = 20
    completed_cells = 0
    latest_done_cells = 0 # re init for each sheet
    
    f_str = 'Sheet {:d}/{:d} | {:' + str(length) + 's} | {:d}/{:d} cells done'

    MyConsoleHandler.change_terminator('\r')

    while any( t.is_alive() for t in thread_list ) or not data_count_queue.empty():
        # While any of the threads is alive
        # ie while atleast one thread is alive
        # or
        # while queue is not empty

        prog = '#' * (counter%(length+1)) + '-' * (length - (counter%(length+1)))
        try:
            latest_done_cells = data_count_queue.get_nowait()
            # Using nowait since during upload,
            # queue takes time to fill up
            # And normal get, blocks until queue gets an item
            # get_nowait either gives a value or an exception
        except queueEmpty as q:
            pass
        else:
            # Only execute if queueEmpty error doesn't occur
            completed_cells += latest_done_cells

        msg = f_str.format(sh_cur, sh_total, prog, completed_cells, total_cells)
        logger.info(msg)

        if not any( t.is_alive() for t in thread_list ):
            # if all threads are dead
            # empty the queue quickly and break out
            logger.debug('All threads are unalive so emptying the queue and breaking out')
            while not data_count_queue.empty():
                completed_cells += data_count_queue.get()
                # Not using get_nowait() here, since
                # at this line, either queue will have items or
                # it will be empty

            # Break out after queue is emptied
            break 

        counter += 1
        time.sleep(interval)


    # Print 100% message
    MyConsoleHandler.restore_terminator()
    prog = '#' * length
    msg = f_str.format(sh_cur, sh_total, prog, completed_cells, total_cells)
    logger.info(msg)

    logger.debug("All threads are aliven't!")

    for t in thread_list:
        # Making certain all threads are stopped
        t.join()
        logger.debug(t.name + ' joined')


def work_divider(no_of_cells, n_threads):
    '''Divide the no of cells almost equally among n_threads

    no_of_cells = The number of cells we need to divide among threads
    n_threads = The number of threads among which we divide the cells
    '''

    # https://math.stackexchange.com/a/1081099
    
    N = no_of_cells
    M = n_threads
    for i, k in enumerate(range(M)):
        start_index = (N * k) // M + 1 # +1 since cells are 1-indexed
        inc = (N *(k+1))//M - start_index 
        end_index = start_index + inc
        
        # i is the thread number
        yield i, start_index, end_index
