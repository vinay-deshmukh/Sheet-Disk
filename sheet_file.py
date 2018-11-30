'''File wrapper class to be used when transfering data
to and from Google Sheets'''

import base64 as b64
from utils import (
        sheet_upload,
        CELL_CHAR_LIMIT,
        CELLS_PER_SHEET,
        CHAR_PER_SHEET
        )

class SheetFile:
    def __init__(self, name, client, content):
        # Get client credentials for managing sheets
        self.gc = client

        # Set file name
        self.name = name

        self.og_content = content

        # Encode the input_file to b64
        bytes_encoded = \
            b64.b64encode(self.og_content)

        # Use repr to get bytes as string
        # [2:-1] to avoid b' and '
        self.encoded = repr(bytes_encoded)[2:-1]


        # List which stores keys of sheets
        self.key_list = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_trace):
        # TODO: Write details of file into JSON file before quitting

        if not self.key_list:
            # if key_list is empty then don't bother saving JSON
            return

        import json
        json_obj = \
            {
                'name' : self.name,
                'key_list': self.key_list
            }
        with open(self.name + ' ' + right_now() + '.json', 'w') as f:
            json.dump(json_obj, f)

        pass

    def chunk_encoded(self):
        return (self.encoded[i:i + CHAR_PER_SHEET]
                    for i in range(0, len(self.encoded), CHAR_PER_SHEET))

    def start_upload(self):

        for sheet_no, wk_content in enumerate(self.chunk_encoded()):
            # Create a sheet for file
            sh = self.gc.create(self.name + ' ' + str(sheet_no) + ' ' + right_now())

            # Share the file so others can also access
            sh.share('None', 'anyone', 'reader')

            # Upload content to file
            wks = sh.sheet1
            sheet_upload(wks, wk_content)

            # Store it's key after successful upload
            self.key_list.append(sh.id)

def right_now():
    '''Return Y:M:D H:M:S'''
    import datetime
    right_now = str(datetime.datetime.now()).replace(':', '-').split('.')[0]
    return right_now

