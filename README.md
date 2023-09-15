# notion-automation

Welcome to the notion automation script! In order to track my life better and make it more structured, I decided to write a daily diary and tracker in Notion - as it is automatically synchronized between different devices (Android/iOS/Windows). The daily tracker is divided into three sections - to-do, tracker, and diary. While not all sections are filled and are meant to be filled automatically, it would be good if the daily tracker pages could be created with daily events populated within the tracker, if they exist.

Since Notion provides API which could be used with Python3, I decided to use notion's API to make a daily page (and a monthly page if it is a new month). 

### Project Structure
![alt text](https://github.com/david4270/notion-automation/blob/main/files/project_flow.png?raw=true)

### Update
##### 230902
- Address time zone differences in some calendar events which is set in different timezone. Special thanks to Tottenham Hotspur Football Club for providing this test case. #COYS

##### 230911
- Script can read To-do list from the most recent diary, and copy it to today's diary.
- Script can read schedule information from the most recent diary, and write the events back to Google Calendar.

##### 230914
- Script can avoid creating duplicate events in Google Calendar, when it is checking the diary from the most recent day before creation of today's diary.
- And... the diary is now divied by 30-minute term!

![alt text](https://github.com/david4270/notion-automation/blob/main/files/monthly.png?raw=true)

Here is what the diary format looks like :D

![alt text](https://github.com/david4270/notion-automation/blob/main/files/diary.png?raw=true)
