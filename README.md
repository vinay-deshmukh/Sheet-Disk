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


# How to install

* Prerequisites:

	This package makes use of `gspread`, which needs OAuth credentials to work. To see how to get them, [Click here](https://github.com/vinay-deshmukh/Sheet-Disk/blob/master/TUTORIAL.md).

	After you download the OAuth credentials file, store it in a safe location. Copy it's path, and create an environment variable, named `SH_DISK_CREDS`.

	For example,

	![Environment variable](https://user-images.githubusercontent.com/32487576/50295990-6c9c3b00-049f-11e9-8635-b1e895ac09bc.png)

To install this package, run:

`pip install sheet_disk`


Requirements: 
* Python 3.6.7+ (May work on lower versions of 3.x, but hasn't been tested on that).
* Windows 10 (May work on Linux, MacOS, and older Windows but it's not been tested on them).

# How to use

## 1. Using as a Command Line Program

	
   ### Uploading a file:
       
      python -m sheet_disk.cli upload <path_to_file>
      

   After uploading has finished, a JSON file ([Click for more details](#json_file)) will be created in your current directory. This file will help you retrieve your uploaded file from Google Sheets. 
      
   
      
   Where,
   
   * path_to_file: The file which you want to upload
         
      Note: **DON'T LOSE THIS JSON FILE. IF YOU LOSE THIS FILE, YOU CAN'T RETRIEVE YOUR UPLOADED FILE.**
      
      Currently, the created sheets files are made public by default, so that you can share your files with friends, by simply sending them the JSON file.([Click for more details](#json_file))
      
   ### Resuming an upload of a file:
   	
    python -m sheet_disk.cli upload <path_to_file> <file_info.json>
    
   Where,

   * file_info.json([Click for more details](#json_file)): **This argument is optional.** If your uploading is cut off before completion, the program will still create a json file, you can pass this json file to resume uploading from that point.

   
    
   ### Downloading a file:
    
     python -m sheet_disk.cli download <download_path> <file_info.json>
        
   Where,
        	
   * download_path = Download location for the file, 
       		
     For Example:
            	C:/Users/Me/file.jpg
                
    * file_info.json = The json file([Click for more details](#json_file)) containing the information about the uploaded file, you got when you uploaded the file
    
   Note: If your download is interrupted for some reason, you can just the run the above command again and Sheet-Disk will resume your download from the last completely downloaded sheet.
    
   #### To see argument usage, use: 
    python -m sheet_disk.cli -h


## 2. Using in a program
	
   For using this package in a program, you can do the following:
    
    >>> import sheet_disk
    >>> 
    >>> # Uploading a file
  	>>> sheet_disk.upload('My File Path.jpg')
  	>>> 
  	>>> # Resuming an upload of file
  	>>> sheet_disk.upload('My File Path.jpg', 'My File Details.json') 
  	>>> 
  	>>> # Download a file
  	>>> sheet_disk.download('My downloaded file.jpg', 'My File Details.json')

    
 
# Sample Usage

* ## CLI:

	* ### Code:
	
		`python -m sheet_disk.cli upload starry_night.jpg`
        
        `python -m sheet_disk.cli download starry_night_download.jpg starry_night.jpg.json`

	* ### Uploading a file:
	
    	Before Uploading:

		![Before Uploading](https://user-images.githubusercontent.com/32487576/50295988-6c03a480-049f-11e9-99f7-3763cd4e5fda.png)

		After Uploading:
        
		![After Uploading](https://user-images.githubusercontent.com/32487576/50295998-6e65fe80-049f-11e9-8eb3-36ab485b554c.png)

	* ### Downloading a file:

		Before Downloading:

		![Before Downloading](https://user-images.githubusercontent.com/32487576/50295987-6c03a480-049f-11e9-91d7-7b623a5bd49b.png)
        
        After Downloading:
        
		![After Downloading](https://user-images.githubusercontent.com/32487576/50295997-6dcd6800-049f-11e9-9b50-d2ee0b2d0688.png)
* ## Program:

	* ### Code:
	
			import sheet_disk
    	    sheet_disk.upload('starry_night.jpg')
        	sheet_disk.download('starry_night_download.jpg', 'starry_night.jpg.json')

	* ### Uploading a file:
	 
       	Before Uploading:

		![Before Uploading](https://user-images.githubusercontent.com/32487576/50297334-9b67e080-04a2-11e9-9254-d63d5a1c8b09.png)
        
        After Uploading:
        
        ![After Uploading](https://user-images.githubusercontent.com/32487576/50295993-6d34d180-049f-11e9-84b1-0b9426bdfd37.png)
    
	* ### Downloading a file:
	
    	Before Downloading:
        
    	![Before Download](https://user-images.githubusercontent.com/32487576/50297337-9c990d80-04a2-11e9-9074-56ff00062ae3.png)
        
        After Downloading:
        
        ![After Download](https://user-images.githubusercontent.com/32487576/50295992-6c9c3b00-049f-11e9-9336-6af03bedf2a5.png)

<a name="json_file"> </a>
# JSON File

Sheet-Disk stores the keys/ids of the spreadsheets, version of the program used when creating the file in a JSON file. This JSON file has the name of your file, and will have a timestamp if a file with the same name exists.

Creation of this file will happen even if the program quits unexpectedly due to an external exception, like if your internet stops working, this file will keep track of the data that has already been uploaded to Sheets. This way you can resume uploading, if the file you were uploading is big.

This JSON file is your only way to access the file contents that you have stored online, so **PLEASE KEEP THIS FILE SAFE!**

You can share this file with your friends to share your uploaded files with your friends.



# Liability

I don't take any liability on the off chance that you are not able to retrieve your file from Sheets. 
Please take multiple backups of your files, in case you are not able to retrieve your files from Google Sheets.