# Sheet Disk

Use Google Sheets as a storage device!

# What is it?

Encode your files into `base64` format and store them in a  Google Sheets spreadsheet in text format!

Google Sheets files don't count towards your Drive Storage, so we create these files without them taking up space on the Drive. So, essentially you can have your data be on google servers but take up 0 bytes.

**Note**: The spreadsheet files are created programmatically, and they are stored under the Service Account you get when you sign up for Google Sheet API credentials (See How to Install section), so you won't be able to see the files in your Google Drive.
You'll only be able to access these files through this program.

# How it works

Each cell can hold 50000 characters, that means each cell can easily hold 50kbytes of your data. But, we need to prepend the `'` character to each cell, so that `=`  doesn't get interpreted as a formula.

Current limit for each cell in the program is 49500 characters, but you could change that to 49998 for more storage.

The hard limit for cells in a Spreadsheet is 2 million cells, but when we fill the cells in such a  dense manner, we can only use about 1000 cells in one spreadsheet file. Hence, your file is broken down in chunks of 1000 * 49500 bytes and stored in separate spreadsheet files.

**Note**: There is a 33% overhead that comes with converting files to their `base64` representation.


# How to install (TODO)

`TODO`: pip install sheet_disk

You'll need `gspread` and `oauth2client`.

Install them:
`pip install gspread oauth2client`

`gspread` needs valid Drive API credentials for use in OAuth2. [How to get them!](https://gspread.readthedocs.io/en/latest/oauth2.html)


Store the JSON file from Google in a safe location.

Create an environment variable: SH_DISK_CREDS, which contains the path to the JSON file.

TODO: Insert image here

Requirements: 
* 3.6+ (May work on lower versions of 3.x, but isn't tested on that.), 
* Windows (May work on Linux, MacOS, but it's not been tested)

# How to use

* You can see the command line usage by using `-h` flag.
1. Using as a Command Line Program _(With arguments)_
	
    * Uploading a file:
       
      ```python sheet_disk.py upload [path_to_file]```
      
      After uploading has finished, a JSON file will be created in your current directory. This file will help you retrieve your uploaded file from Google Sheets. 
      
      Note: **DON'T LOSE IT. IF YOU LOSE THIS FILE, YOU CAN'T RETRIEVE YOUR FILE.**
    
    * Downloading a file:
    
     	```python sheet_disk.py download [download_path.extension] [file_info.json]```
        
        Where,
        	
         * download_path.extension = Download location of the file
            
         * file_info.json = The json file containing the information about the uploaded file, you got when you uploaded the file
     
    
    
2. `TODO` Using as a Command Line Program _(Without arguments)_
	
    This mode is same as the above mode, only difference being, in this mode, the program will prompt you for it
   's command line arguments instead of  you passing them in the command.
 
# Sample Usage

`TODO`

`TODO`: Also, add sample files showing how to interact with the module, ie 
	
    python -c module arg1 arg 2
    

# Liability

I don't take any liability on the off chance that you are not able to retrieve your file from Sheets. 
Please take multiple backups of your files, in case you are not able to retrieve your files from Google Sheets.