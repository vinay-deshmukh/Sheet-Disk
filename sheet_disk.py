'''Main file to run when running this program'''
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sheet_file import SheetFile

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# Insert your credentials file name here
creds_file = 'credentials.json'
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
gc = gspread.authorize(creds)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="Path of the file you want to upload")
    args = parser.parse_args()
    # TODO: Parse windows path correctly
    print('File to upload:', args.file_path)
    file_to_upload = args.file_path
    # def upload_file

    # Create SheetFile
    with open(file_to_upload, 'rb') as f:
        content = f.read()
    # TODO: Obtain correct filename
    filename = file_to_upload.split(r'\\')[-1]


    with SheetFile(name=filename,
            client=gc, content=content) as sheet:
        sheet.start_upload()

