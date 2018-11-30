'''Main file to run when running this program'''
import os, sys
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sheet_file import SheetFile

# Logging setup
logger = logging.getLogger('sheet_disk.py')
logger.setLevel(logging.DEBUG)

# Handlers
c_handler = logging.StreamHandler(sys.stdout)
c_handler.setLevel(logging.DEBUG)

# Formatter
c_format = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(funcName)s - %(message)s')
c_handler.setFormatter(c_format)

# Add handlers to the logger
logger.addHandler(c_handler)

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# Insert your credentials file name here
creds_file = 'credentials.json'
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

def upload_file(user_file, json):
    # When uploading a file
    # if JSON file is specified,
    # then file upload is to be resumed
    # otherwise fresh upload is to be started

    if json is None:
        # fresh upload
        logger.info('Performing Fresh Upload!')
        with open(user_file, 'rb') as f:
            logger.info('Reading file content!')
            content = f.read()

        # Get basename for user file
        base_name = os.path.basename(user_file)

        with SheetFile(name=base_name,
                client=gc, content=content) as sheet:
            logger.info('Starting upload now!')
            sheet.start_upload()
            logger.info('File upload complete!')
    else:
        # Resume upload
        raise NotImplementedError('Resume upload not implemented yet')


def download_file(user_file, json):
    # Download file via JSON data
    # user_file is path of the downloaded file
    raise NotImplementedError('Download not implemented yet')

def main():
    # Get parser object
    logger.debug('Getting parser')
    parser = get_parser()
    args = parser.parse_args()
    logger.debug('Args have been parsed')

    # Error handling
    logger.debug('Start error handling')
    if args.method == 'download' and not args.json:
        # if downloading, json needs to be specified
        parser.error('Need to specify JSON file, when downloading')
    # TODO: Verify if paths are correct, and json file is proper
    logger.debug('No errors found')

    # MAIN START
    method = args.method
    user_file = args.file
    json = args.json

    if method == 'upload':
        logger.debug('Start upload')
        upload_file(user_file, json)
        logger.info('Upload is done!')

    elif method == 'download':
        logger.debug('Start download')
        download_file(user_file, json)
        logger.info('Download is done')


if __name__ == '__main__':
    main()
