'''Main file to run when running this program'''

import os
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

    parser.add_argument('method',
        help='Specify download/upload action on file',
        choices=['download', 'upload'])

    parser.add_argument('file',
        help='File to be uploaded / downloaded')

    parser.add_argument('json',
        nargs='?',
        help='Path to JSON file which contains information to download the file.',)

    return parser

def upload_file(user_file, json_file=None):
    # When uploading a file
    # if JSON file is specified,
    # then file upload is to be resumed
    # otherwise fresh upload is to be started

    if json_file is None:
        # fresh upload
        logger.info('Performing Fresh Upload!')
        with open(user_file, 'rb') as f:
            logger.info('Reading file content!')
            content = f.read()

        # Get basename for user file
        base_name = os.path.basename(user_file)

        with SheetUpload(name=base_name,
                client=gc, content=content) as sheet:
            logger.info('Starting upload now!')
            sheet.start_upload()
            logger.info('File upload complete!')
    else:
        # Resume upload
        raise NotImplementedError('Resume upload not implemented yet')


def download_file(user_file, json_file):
    # Download file via JSON data
    # user_file is path of the downloaded file

    import json
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

    # Error handling
    logger.debug('Start error handling')
    if args.method == 'download' and not args.json:
        # if downloading, json needs to be specified
        logger.error('Need to specify JSON file, when downloading')
    # TODO: Verify if paths are correct, and json file is proper
    logger.debug('No errors found')

    # MAIN START
    method = args.method
    user_file = args.file
    json = args.json

    if method == 'upload':
        logger.info('Start upload')
        upload_file(user_file, json)
        logger.info('Upload is done!')

    elif method == 'download':
        logger.info('Start download')
        download_file(user_file, json)
        logger.info('Download is done')


if __name__ == '__main__':
    main()
