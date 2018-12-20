# Tutorial: How to get OAuth Credentials

## Step 1 of 3: Create a Project

![Image 1](https://user-images.githubusercontent.com/32487576/50293634-17115f80-049a-11e9-9821-bd4b8fc2c5f7.png)

1. Go to [Google Developers Console](https://console.developers.google.com/cloud-resource-manager).
2. Click on `CREATE PROJECT`

![Image 2](https://user-images.githubusercontent.com/32487576/50293635-17115f80-049a-11e9-80f5-45ec610d88ba.png)

3. Enter the name of the project. You can enter `Sheet-Disk`. You can leave Location as it is. 
4. Click on `CREATE`.

![Image3](https://user-images.githubusercontent.com/32487576/50293636-17115f80-049a-11e9-9f8e-6bfbddf70dcf.png)

5. Click on project name to go to the next step.

## Step 2 of 3: Creating a Service Account

![Image 4](https://user-images.githubusercontent.com/32487576/50293637-17a9f600-049a-11e9-8b87-97e43fdf84ed.png)

1. When you land on the page, you need to click on `Select a project`. This will open a new window where you can select your project.
2. Select `Sheet-Disk`.
3. Click on `OPEN`. This will open the following page.

![Image 5](https://user-images.githubusercontent.com/32487576/50293638-17a9f600-049a-11e9-80ec-f73e312cf9b7.png)
4. Click on `Google APIs`. This will open the next screen.

![Image 6](https://user-images.githubusercontent.com/32487576/50293640-18428c80-049a-11e9-88e8-274e669ef1f8.png)
5. Click on `Credentials` tab.
6. Click on `Create Credentials`.
7. Select `Service Account key`.

![Image 7](https://user-images.githubusercontent.com/32487576/50293641-18428c80-049a-11e9-90d5-95e1e3a0088d.png)
8. Enter a name for the service account. I have used `sheet-disk0`.
9. Set it's role as `Project > Editor`.
10. Select `JSON` as Key type.
11. Click on `Create`. Now, you can download the JSON file.

![Image 8](https://user-images.githubusercontent.com/32487576/50293642-18db2300-049a-11e9-968e-d3e6612bea92.png)
12. Save the `.json` file in a suitable location.

![Image 9](https://user-images.githubusercontent.com/32487576/50293644-18db2300-049a-11e9-9ab4-bdac9cdefe19.png)
13. Close the pop up box.
14. Click on `Google APIs` to go back to go to the next step.


## Step 3 of 3: Adding APIs to the project

![Image 10](https://user-images.githubusercontent.com/32487576/50293645-18db2300-049a-11e9-8a4d-79b24b7ba06b.png)
1. Click on `Library` tab to search for APIs.

![Image 11](https://user-images.githubusercontent.com/32487576/50293649-1973b980-049a-11e9-8ad2-ca8a0c4b9250.png)
2. Search for `drive api`.

![Image 12](https://user-images.githubusercontent.com/32487576/50293650-1973b980-049a-11e9-962f-082a3a33fde2.png)
3. Select `Google Drive API`.

![Image 13](https://user-images.githubusercontent.com/32487576/50293652-1a0c5000-049a-11e9-9544-63d9e18725b0.png)
4. Click on `Enable`.

![Image 14](https://user-images.githubusercontent.com/32487576/50293654-1a0c5000-049a-11e9-896d-a7110a847048.png)
5. On the next screen, click on `Create Credentials`.

![Image 15](https://user-images.githubusercontent.com/32487576/50293655-1a0c5000-049a-11e9-86ee-6647ac16768f.png)
6. Use the above settings in the next screen, and click on the blue button.

![Image 16](https://user-images.githubusercontent.com/32487576/50293656-1aa4e680-049a-11e9-9bd8-50c8f1e86a29.png)
7. Click `Done` at the next screen. 


![Image 17](https://user-images.githubusercontent.com/32487576/50293657-1aa4e680-049a-11e9-9af0-069e7470d9ed.png)
8. Repeat steps 1-7 for `Sheets API`.





