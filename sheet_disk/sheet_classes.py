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

        for sheet_no, wk_content in enumerate(self.gen_encoded()):

            if self.j_details and sheet_no < prev_uploaded_sheets:
                # Only check for prev_uploaded_sheets,
                # if self.j_details is not None

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
            sheet_upload(wks, wk_content)
            logger.info('Sheet ' + str(sheet_no) + ' uploaded correctly!')

            # Store it's key after successful upload
            self.key_list.append(sh.id)
            # Delete last_key since sheet was written successfully
            self.last_key = None

class SheetDownload:
    def __init__(self, client, download_path, json_dict):
        
        self.gc = client
        self.download_path = download_path
        self.key_list = json_dict['key_list']
        self.b64_file = download_path + '.b64'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_trace):
        
        if os.path.exists(self.b64_file):
            # Delete b64 file on cleanup
            logger.debug('Deleting ' + self.b64_file)
            os.remove(self.b64_file)

    def start_download(self):

        with open(self.b64_file, 'w') as b64_file:
            # Write to b64_file in chunks

            for n_key, key in enumerate(self.key_list):

                logger.debug('Open sheet ' + str(n_key))
                sh = self.gc.open_by_key(key)
                wk = sh.sheet1

                logger.debug('Start download of sheet ' + str(n_key))
                sheet_content = sheet_download(wk)

                logger.debug('Write downloaded content to b64 file')
                for one_cell in sheet_content:
                    b64_file.write(one_cell)

        logger.info('Encoded file created!')
        logger.info('Now, starting decoding!')
        self.decode_file()

    def decode_file(self):
        with open(self.download_path, 'wb') as down,\
                open(self.b64_file     , 'r') as b64_f:
            # Read from encoded file, convert to literal bytes
            # And write to download_path

            # TODO: Introduce chunking here
            # Read string form of bytes, and convert to actual bytes
            bytes_b64 = bytes(b64_f.read(), 'ascii')

            # Decode b64 back to original encoding
            decoded_bytes = base64.b64decode(bytes_b64)
            down.write(decoded_bytes)

        logger.info('File has been decoded!')


def right_now():
    '''Return Y:M:D H:M:S'''
    import datetime
    right_now = str(datetime.datetime.now()).replace(':', '-').split('.')[0]
    return right_now

