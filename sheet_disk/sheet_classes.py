'''File wrapper classes to be used when transfering data
to and from Google Sheets'''

import os, sys
import base64
from .my_logging import get_logger
from .utils import (
        sheet_upload,
        sheet_download,
        CELL_CHAR_LIMIT,
        CELLS_PER_SHEET,
        CHAR_PER_SHEET,
        )

logger = get_logger()

class SheetUpload:
    def __init__(self, name, client, content):

        logger.debug('Start SheetUpload init')
        # Get client credentials for managing sheets
        self.gc = client

        # Set file name
        self.name = name

        # TODO: Don't read file content as one string, split into calls of f.read()
        self.og_content = content

        # Encode the input_file to b64
        bytes_encoded = \
            base64.b64encode(self.og_content)

        # Use repr to get bytes as string
        # [2:-1] to avoid b' and '
        self.encoded = repr(bytes_encoded)[2:-1]


        # List which stores keys of sheets
        self.key_list = []

        # Latest key for sheet(which may get quit)
        self.last_key = None

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
                        'File may not have been uploaded completely.')

        if exc_type and self.last_key:
            # if exception occurs, delete the last spreadsheet
            logger.debug('Deleting latest key, since exception has occured')
            self.gc.del_spreadsheet(self.last_key)

        import json
        json_obj = \
            {
                'name' : self.name,
                'key_list': self.key_list,
                # TODO: Add valid parameter to signify if file was uploaded in its entirety
            }
        
        json_filename = self.name + '.json'
        if os.path.exists(json_filename):
            logger.debug('JSON file already exists, creating new with timestamp')
            json_filename = json_filename.replace('.json', ' ' + right_now() + '.json')

        with open(json_filename, 'w') as f:
            logger.info('Writing json file')
            json.dump(json_obj, f)


    def chunk_encoded(self):
        return (self.encoded[i:i + CHAR_PER_SHEET]
                    for i in range(0, len(self.encoded), CHAR_PER_SHEET))

    def start_upload(self):
        for sheet_no, wk_content in enumerate(self.chunk_encoded()):
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

