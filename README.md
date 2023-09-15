# Project DiarySetup

Welcome to the notion automation script! To track my life better and make it more structured, I started to write a daily diary and tracker in Notion - as Notion is automatically synchronized between different devices (Android/iOS/Windows). The daily tracker is divided into three sections - to-do, tracker, and diary. While not all sections are filled and are meant to be filled automatically, it would be good if the daily tracker pages could be created with daily events populated within the tracker, if they exist.

Since Notion provides API which could be used with Python3, I decided to use notion's API to make a daily page (and a monthly page if it is a new month). The script started working on July 22, 2023, and more features have been added.

## Project Structure
Here is a brief overview of how this project is structured. The script finds today's date and checks if the monthly database exists. 

If the monthly database does not exist, it looks into the previous month's database and searches the most recent diary (within the selected range, set as ten days). If the recent diary is found, it retrieves information from the diary (to-do lists and schedule), then creates events in Google Calendar if the new schedule entry is found in Notion. Then, it creates the monthly database for this month.

Then (or if a monthly database already existed), it retrieves the diary template, checks today's events from Google Calendar, and checks if today's diary is already created.

If today's diary is not created, the script searches for the most recent diary, the same as the previous loop when the monthly database did not exist. Then, it creates a daily diary for the day.

If you want a graphic version of this description, check below:

![alt text](https://github.com/david4270/notion-automation/blob/main/files/project_flow.png?raw=true)

## Update
### 230902
- Address time zone differences in some calendar events set in different time zones. Special thanks to Tottenham Hotspur Football Club for providing this test case. #COYS

### 230911
- Script can read a To-do list from the most recent diary and copy it to today's diary.
- Script can read schedule information from the most recent diary and return the events to Google Calendar.

### 230914
- Script can avoid creating duplicate events in Google Calendar when checking the diary from the most recent day before the creation of today's diary.
- And... the schedule is now divided by 30 minutes!

## Diary Structure
The diary is contained in the 'monthly databases' - as below:

<img src="https://github.com/david4270/notion-automation/blob/main/files/monthly.png?raw=true" width="50%">

Here is what the diary format looks like - it includes To-Do, Tracker, and Diary.

<img src="https://github.com/david4270/notion-automation/blob/main/files/diary.png?raw=true" width="50%">

