'''File wrapper classes to be used when transfering data
to and from Google Sheets'''

import os, sys, json
from functools import partial
import base64
from .my_logging import get_logger
from .__version__ import __version__
from .utils import (
        sheet_upload,
        sheet_download,
        CELL_CHAR_LIMIT,
        CELLS_PER_SHEET,
        CHAR_PER_SHEET,
        )

logger = get_logger()

class SheetUpload:
    def __init__(self, name, client, upload_file_path, json_file=None):

        logger.debug('Start SheetUpload init')
        # Get client credentials for managing sheets
        self.gc = client

        # Set file name
        self.name = name

        # Store file path, to retrieve data from when upload starts
        self.upload_file_path = upload_file_path

        # List which stores keys of sheets
        self.key_list = None

        # No of sheets this file will need
        self.n_sheets = None

        # Latest key for sheet(which may get quit)
        self.last_key = None

        # Dict that will hold the json file's attributes
        self.j_details = None
        if json_file:
            # Resumable upload section
            logger.info('Resuming upload!')
            with open(json_file) as f:
                self.j_details = json.load(f)

            # Read key_list from j_details
            # Get the keys which were previously uploaded
            self.key_list = self.j_details['key_list']

            # Get n_sheets from j_details
            self.n_sheets = self.j_details['n_sheets']

        else:
            logger.info('Fresh upload')

            # Init list to empty for fresh upload
            self.key_list = []

            # Only calculate the no of sheets if it's a fresh upload
            input_size = os.stat(self.upload_file_path).st_size
            from math import ceil
            b64_size = 4 * ceil(input_size / 3)
            self.n_sheets = ceil(b64_size / CHAR_PER_SHEET)
        
        logger.debug('Key list size : ' + str(len(self.key_list)))
        logger.info('Total sheets needed: ' + str(self.n_sheets))


        logger.debug('SheetUpload Init complete')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_trace):

        if not self.key_list:
            # if key_list is empty then don't bother saving JSON
            logger.debug('Key list is empty, so not saving JSON')
            return

        if exc_type:
            # exception has occured, which means file may not have completely uploaded
            logger.info(str(exc_type) + ' Exception has occured.'
                        ' File may not have been uploaded completely.')

        if exc_type and self.last_key:
            # if exception occurs, delete the last spreadsheet
            logger.debug('Deleting latest key, since exception has occured')
            self.gc.del_spreadsheet(self.last_key)

        complete_upload = False
        if self.n_sheets == len(self.key_list):
            # File was completely uploaded
            complete_upload = True

        import json
        json_obj = \
            {
                'name' : self.name,
                'complete_upload': complete_upload,
                'n_sheets': self.n_sheets,
                'key_list': self.key_list,
                'version': __version__,
                # TODO: Add valid parameter to signify if file was uploaded in its entirety
            }
        
        json_filename = self.name + '.json'
        if os.path.exists(json_filename):
            logger.debug('JSON file already exists, creating new with timestamp')
            json_filename = json_filename.replace('.json', ' ' + right_now() + '.json')

        with open(json_filename, 'w') as f:
            logger.info('Writing json file')
            json.dump(json_obj, f, indent=4)

    def gen_encoded(self):
        with open(self.upload_file_path, 'rb') as f:
            
            # Read in terms of total bytes we can fit in one sheet
            # b64 gives 4 bytes for input 3 bytes,
            # so calculate input size such that b64 is CHAR_PER_SHEET
            chunk_size =  CHAR_PER_SHEET // 4 * 3

            for byte_chunk in iter(partial(f.read, chunk_size), b''):
                # Encode file bytes to base64
                enc64 = base64.b64encode(byte_chunk)

                # Get string from base64 bytes
                yield enc64.decode('ascii')

    def start_upload(self):
        if self.j_details:
            # Get previously uploaded sheets
            prev_uploaded_sheets = len(self.j_details['key_list'])

        for sheet_no, wk_content in enumerate(self.gen_encoded(), 1):
            # Enumerate from 1 so 
            # progress is shown as as 1/5, and not 0/5

            if self.j_details and sheet_no < prev_uploaded_sheets + 1:
                # Only check for prev_uploaded_sheets,
                # Use +1 since index is starting at 1
                # So Progress is shown as 1/5, and not 0/5

                # Skipping sheet which previously exists
                logger.info('Sheet ' + str(sheet_no) + ' already exists!')
                logger.info('Skipping sheet ' + str(sheet_no))
                continue

            # Create a sheet for file
            logger.info('Creating sheet ' + str(sheet_no))
            sh = self.gc.create(self.name + ' ' + str(sheet_no) + ' ' + right_now())

            # Share the file so others can also access
            sh.share('None', 'anyone', 'reader')
            self.last_key = sh.id

            # Upload content to file
            wks = sh.sheet1
            logger.info('Writing data to sheet ' + str(sheet_no))

            sheet_upload(wks, wk_content, 
                    sheet_progress=(sheet_no, self.n_sheets))

            logger.info('Sheet ' + str(sheet_no) + ' uploaded correctly!')

            # Store it's key after successful upload
            self.key_list.append(sh.id)
            # Delete last_key since sheet was written successfully
            self.last_key = None

class SheetDownload:
    def __init__(self, client, download_path, json_dict):

        if not json_dict['complete_upload']:
            # Stop download if file isn't originally uploaded completely
            msg = 'File encoded in JSON file wasn\'t uploaded completely!'
            logger.error(msg)
            raise ValueError(msg)


        self.gc = client
        self.download_path = download_path
        self.key_list = json_dict['key_list']
        self.n_sheets = json_dict['n_sheets']


        self.sheet_progress_file = download_path + '.progress' + '.b64'
        '''
        This file will be created only if doesn't exist.

        This file will store progress in the following format:
        If n_sheets == 4:
        self.sheet_progress_file:
        0000
        // No newline at the end

        0 = Sheet hasn't been downloaded
        1 = Sheet has been downloaded completely, and should not be downloaded again

        At initialization, this file should be read to determine which sheets need to be downloaded again

        // in exit
        if file is made of completely zeroes, then progress file will be deleted.
        Even if there is a single one, the progress file will be saved.
        '''
        if not os.path.exists(self.sheet_progress_file):
            with open(self.sheet_progress_file, 'w') as f:
                # Create 0's for all sheets
                f.write('0' * self.n_sheets)


        # Create list to hold temp files to store progress
        self.sheet_files = []
        '''
        This list will contains paths of the files which are used to download
        sheets into,
        and status of the sheet, denoting whether sheet has been downloaded or not
        '''
        with open(self.sheet_progress_file, 'r+') as f:
            # Read sheet progress from file

            for i in range(1, self.n_sheets + 1):
                # Start sheet counter at 1, not 0

                f.seek(i-1, 0) # Go to i-1 from start
                filename = download_path + '.sheet' + str(i) + '.b64'
                # Convert the 1 or 0 from file to boolean
                done = bool(int(f.read(1)))

                self.sheet_files.append( (filename, done) )
        
        # Boolean to signify if decoding is complete
        # We use this to delete progress file
        self.decoding_complete = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_trace):

        with open(self.sheet_progress_file, 'r') as f:
            # Get sheet file statuses from progress file
            filestatus = [bool(int(i)) for i in f.read()]

        if not any(filestatus):
            # if any of the status is not true,
            # that means no sheet was downloaded correctly
            # So delete progress file
            
            logger.info('No sheets were downloaded completely!')
            logger.info('Deleting progress file')
            os.remove(self.sheet_progress_file)

        elif all(filestatus):
            # If all files are downloaded
            # Check if all have been decoded
            if self.decoding_complete:
                # if decoding is done,
                # then delete sheet and progress files

                logger.info('Deleting progress file')
                os.remove(self.sheet_progress_file)

                for fi, file_and_bool in enumerate(self.sheet_files, 1):
                    file, _ = file_and_bool
                    # _ is used to ignore the bool available with sheet file
                    # see declaration of self.sheet_files for more details
                    logger.info('Deleting sheet file' + str(fi))
                    os.remove(file)

    def start_download(self):

        for sheet_no, key in enumerate(self.key_list, 1):
            # Start sheet_no at 1
            # so output is 
            # 1/5 and not 0/5

            # Get current sheet file path, and status
            current_sheet_path, status = self.sheet_files[sheet_no - 1]

            # Check whether current sheet has already been downloaded
            if status:
                logger.info('Sheet ' + str(sheet_no) + ' has already been downloaded!')
                logger.info('Skipping sheet ' + str(sheet_no))
                continue

            logger.debug('Open sheet ' + str(sheet_no))
            sh = self.gc.open_by_key(key)
            wks = sh.sheet1

            logger.debug('Start download of sheet ' + str(sheet_no))
            sheet_content = \
                sheet_download(
                    wks, 
                    current_sheet=sheet_no
                    )

            # write the data into appropriate sheet file
            with open(current_sheet_path, 'w') as file_current:

                _first = False # Check if first iteration of loop
                for one_cell in sheet_content:
                    file_current.write(one_cell)
                    if not _first:
                        # Display this message only after download has started
                        logger.debug('Writing downloaded content to sheet ' 
                                        + str(sheet_no) + ' file')
                        _first = True

            # After writing to file has been complete
            # Set flag in progress file
            with open(self.sheet_progress_file, 'r+') as f:
                # Go to sheet_no-1 char of file, from start of file
                # Since sheet_no is 1-indexed
                f.seek(sheet_no - 1, 0)
                f.write('1') # Flag current sheet as done
                logger.info('Sheet ' + str(sheet_no) + ' content has been saved!')


        logger.info('Encoded file(s) created!')
        logger.info('Now, starting decoding!')
        self._decode_file()

    def _decode_file(self):
        with open(self.download_path, 'wb') as down:
            # Read from encoded sheet file(s),
            # Convert to literal bytes and then to base64
            # And write to download_path

            chunk_size = 10 * (10 ** 6)  # 10 megabyte
            chunk_size = chunk_size * 4
            # 4 b64 bytes for every 3 input bytes
            # hence, force chunk_size to be multiple for 4

            for chunk in self._multi_file_serial_read(
                                self.sheet_files, 
                                chunk_size=chunk_size
                                ):
                
                # Read string form of bytes, and convert to actual bytes
                bytes_b64 = bytes(chunk, 'ascii')

                # Decode b64 back to original encoding
                decoded_bytes = base64.b64decode(bytes_b64)
                
                down.write(decoded_bytes)

        logger.info('File has been decoded!')
        self.decoding_complete = True
        

    def _multi_file_serial_read(self, list_files, chunk_size):

        class SerialChunkFile:
            __slots__ = 'file', 'position'
            def __init__(self, file, position):
                self.file = file
                self.position = position

        content_list = []
        for file, _ in list_files:
            # _ is used to ignore the bool available with sheet file
            # see declaration of self.sheet_files for more details
            content_list.append( SerialChunkFile(file, 0) )
            # 0 denotes beginning of file

        ci = 0
        while True:
            cur_content1 = content_list[ci] 
            with open(cur_content1.file) as f:
                f.seek(cur_content1.position, 0)
                data = f.read(chunk_size)
                cur_content1.position = f.tell()

            if len(data) < chunk_size:
                ci += 1
                if ci < len(content_list):
                    cur_content2 = content_list[ci]
                    with open(cur_content2.file) as f:

                        f.seek(cur_content2.position, 0)
                        data = data + f.read( chunk_size - len(data) )
                        cur_content2.position = f.tell()
                else:
                    # Restore ci to last index
                    ci -= 1

            if not data:
                logger.debug('All files read')
                break

            yield data

        
def right_now():
    '''Return Y:M:D H:M:S'''
    import datetime
    right_now = str(datetime.datetime.now()).replace(':', '-').split('.')[0]
    return right_now

