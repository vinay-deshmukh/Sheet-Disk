'''Main file to run when running this program'''

import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from .sheet_classes import SheetUpload, SheetDownload
from .my_logging import get_logger

logger = get_logger()

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# Get credentials file from environment variable
creds_file = os.environ.get('SH_DISK_CREDS', None)

if creds_file is None:
    raise KeyError(
        '''Set up environment variable: 'SH_DISK_CREDS' 
        with the path to your Google Sheets API JSON file.

        Refer to README.md for more info.''')

creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
gc = gspread.authorize(creds)

def get_parser():
    import argparse
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(
        dest='action',
        help='Choose from the following:',
        metavar='action')
    subparsers.required = True

    # Upload
    parser_upload = subparsers.add_parser(
        'upload', 
        help='Upload a file to Google Sheets')

    parser_upload.add_argument(
        'upload_file',
        help='File to be uploaded')

    parser_upload.add_argument(
        'upload_json',
        help='JSON file to be passed for resuming an upload',
        nargs='?')


    # Download
    parser_download = subparsers.add_parser(
        'download',
        help='Download a file from Google Sheets')

    parser_download.add_argument(
        'download_file',
        help='Path where file is to be downloaded')

    parser_download.add_argument(
        'download_json',
        help='Path to JSON file which contains file details')

    # Delete
    parser_delete = subparsers.add_parser(
            'delete', 
            help='(Not implemented) Delete a file from Google Sheets')
    parser_delete.add_argument(
            'json_file',
            help='JSON file which contains details of the file')

    return parser

def upload(user_file, json_file=None):
    # When uploading a file
    # if JSON file is specified,
    # then file upload is to be resumed
    # otherwise fresh upload is to be started

    # if json_file is None:
    # fresh upload
    #logger.info('Performing Fresh Upload!')

    # Get basename for user file
    base_name = os.path.basename(user_file)

    with SheetUpload(
            name=base_name,
            client=gc, 
            upload_file_path=user_file, 
            json_file=json_file) as sheet:
        sheet.start_upload()


def download(user_file, json_file):
    # Download file via JSON data
    # user_file is path of the downloaded file

    with open(json_file) as f:
        json_dict = json.load(f)

    # Create sheet file from json
    with SheetDownload(client=gc,
        download_path=user_file, json_dict=json_dict) as f:
        f.start_download()

def main(raw_args=None):
    '''This method is the public interface to sheet_disk functions'''

    # raw_args
    # https://stackoverflow.com/questions/44734858/python-calling-a-module-that-uses-argparser

    # Get parser object
    logger.debug('Getting parser')
    parser = get_parser()
    args = parser.parse_args(raw_args)
    logger.debug('Args have been parsed')
    dargs = vars(args)

    # Error handling
    logger.debug('Start error handling')
    if dargs['action'] == 'upload':
        if not os.path.exists(dargs['upload_file']):
            logger.error(dargs['upload_file'] + ' file doesn\'t exist!')
            raise FileNotFoundError(dargs['upload_file'])

        if dargs.get('upload_json', False):
            # Only enter this block, if 'upload_json' exists
            if not os.path.exists(dargs['upload_json']):
                logger.error(dargs['upload_json'] + 'doesn\'t exist!')
                raise FileNotFoundError(dargs['upload_json'])
            with open(dargs['upload_json']) as f:
                # Will throw json error if file is not valid
                try: json.load(f)
                except json.JSONDecodeError as j:
                    logger.error(dargs['upload_json'] + ' is not a valid JSON file')
                    raise j

    if dargs['action'] == 'download':

        if not os.path.exists(dargs['download_json']):
            logger.error(dargs['download_json'] + ' file doesn\'t exist!')
            raise FileNotFoundError(dargs['download_json'])

        with open(dargs['download_json']) as f:
            try: json.load(f)
            except JSON.JSONDecodeError as j:
                logger.error(dargs['download_json'] + ' is not a valid JSON file')
                raise j

    if dargs['action'] == 'delete':
        raise NotImplementedError()

    logger.debug('No errors found')

    # MAIN START
    
    if dargs['action'] == 'upload':
        logger.info('')
        # Create space

        logger.info('Starting upload...')

        up_file = dargs['upload_file']
        up_json = dargs['upload_json']

        upload(up_file, up_json)
        logger.info('File upload is complete!')

    elif dargs['action'] == 'download':
        logger.info('')
        # Create space

        logger.info('Starting download...')

        down_file = dargs['download_file']
        down_json = dargs['download_json']

        download(down_file, down_json)
        logger.info('File download is complete!')

    elif dargs['action'] == 'delete':
        raise NotImplementedError()

    else:
        raise ValueError('Invalid parameters')

if __name__ == '__main__':
    main()
