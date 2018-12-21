
Release History
=================================

0.1 (2018-12-21)
--------------------

- Chunking of files when uploading and downloading
	* Now, files of any size can be uploaded, and downloaded. Previously, this was limited to the size of user's RAM
- Using multiple threads to speed up downloading and uploading
- Improved CLI parsing
- Refactor the main functions(upload_file to upload, download_file to download)
- Use indent in JSON file for better readability
- Include version and other metadata in JSON file
- Resumable Upload & Download
- Progress bar for uploading, downloading
- Beautify console outputs
- Add tutorial for getting OAuth credentials


0.0.0.2 (2018-12-06)
--------------------

- Can upload, download files
- Can use as a included package, or a CLI app
- JSON file contains name, key list
