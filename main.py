# Notion automation - create diary page every day (copy existing format), with proper date format (Month Day (??Day)) and category (Month YYYY)
# Check google calendar, outlook etc, and retrieve the schedules of the day, populate in the table of the diary (if possible)
# Ideal if it can run every hour when desktop is on, and keep updating the schedule based on google calendar and outlook
# The script should run every morning

# To-do
# 1) Get page data for last 10 days (before today's page creation) - get the latest page. Copy the to-do list and retrieve the modified schedule information from table
# 1-1) Copy the recent to-do list to today's page
# 1-2) Create events (of past) based on schedule information retrieved from 1) on google calendar. If there are multiple events, separate by comma (,)
# 2) Make tables into 30-minute basis, and use 24-hour format


# Notion API
# https://developers.notion.com/docs/create-a-notion-integration
# https://developers.notion.com/reference/post-database-query
# https://www.youtube.com/watch?v=M1gu9MDucMA&ab_channel=PatrickLoeber

# Google API
# https://developers.google.com/calendar/api/quickstart/python
# https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/index.html

import requests
from datetime import datetime, timezone, timedelta
from dateutil.tz import *

import json

import src.notionapi as notionapi
import src.apiimport as apiimport
import src.datahandling as datahandling
import src.gcalapi as gcalapi

def main():
    # Common headers
    headers = {
        "Authorization": "Bearer " + apiimport.NOTION_TOKEN,
        "accept": "application/json",
        "Notion-Version": "2022-06-28",
        "content-type": "application/json"
    }

    #testcase
    now = datetime(2023,9,12)

    # Analyse datetime
    #now = datetime.now(tzlocal())  
    print("Now: ", now)
    today_diary_name = now.strftime("%B %d (%a)")
    print("Formatted time: ", today_diary_name)
    today_folder = now.strftime("%B %Y")
    print("New calendar goes into: ", today_folder)

    # Search range for previous documents - 10 days?
    prev_searchrange = now - timedelta(days=10)
    prev_searchrange_name = prev_searchrange.strftime("%B %d (%a)")
    print("Search from: ",prev_searchrange_name)
    prev_folder = prev_searchrange.strftime("%B %Y")

    # query

    query_url = f"https://api.notion.com/v1/databases/{apiimport.DATABASE_ID}/query"
    query_payload = {"page_size": 100}

    pages = notionapi.query_pages(query_url, apiimport.DATABASE_ID, query_payload, headers)
    titles = datahandling.retrieveInfo(pages)

    to_do_backup = []

    # Check if the monthly folder (today_folder) exists - if not, need to create database
    if today_folder not in titles.keys():
        print("Nope - this month's folder not found")
        
        if prev_folder in titles.keys():
            print("Searching last month's folder for syncing data...")
            
            # retrieve diaries' names from previous month
            retrieve_id = titles[prev_folder][1].replace("-","")
            retrieve_url = f"https://api.notion.com/v1/databases/{retrieve_id}/query"

            pages = notionapi.query_pages(retrieve_url, retrieve_id, query_payload, headers)

            titles = datahandling.retrieveInfo(pages)

            queryday = now.replace(day=1) # 1st of this month
            
            while queryday != prev_searchrange:
                queryday -= timedelta(days=1)
                queryday_diary_name = queryday.strftime("%B %d (%a)")
                print(queryday_diary_name)
                # perform query
                if queryday_diary_name in titles.keys():
                    print("target diary found")
                    # query content of the diary
                    target_diary_id = titles[queryday_diary_name][1].replace("-","")
                    target_diary_url = f"https://api.notion.com/v1/blocks/{target_diary_id}/children"
                    target_diary_data = notionapi.get_data(target_diary_url, headers)
                    for datalet in target_diary_data:
                        #print(datalet)
                        if 'to_do' in datalet.keys():
                            datalet['to_do']['checked'] = False
                            if datalet['has_children'] == True:
                                target_child_id = datalet['id'].replace("-","")
                                target_child_url = f"https://api.notion.com/v1/blocks/{target_child_id}/children"
                                target_child_data = notionapi.get_data(target_child_url, headers)
                                
                                children_data = []
                                for it in range(len(target_child_data)):
                                    interim_data = {}
                                    interim_data['type'] = target_child_data[it]['type']

                                    if target_child_data[it]['type'] == 'image':
                                        continue

                                    interim_data[interim_data['type']] = target_child_data[it][interim_data['type']]

                                    if target_child_data[it]['type'] == 'to_do':
                                        interim_data[interim_data['type']]['checked'] = False
                                    
                                    children_data.append(interim_data)
                                

                                datalet['to_do']['children'] = children_data
                                
                            # Gotta deal with children
                            to_do_backup.append(datalet)


                    break
                    
        # Create database - https://www.pynotion.com/create-databases/
        create_payload = notionapi.empty_database_format(apiimport.DATABASE_ID, today_folder)

        create_url = "https://api.notion.com/v1/databases"

        notionapi.create_pages(create_url, create_payload, headers)
        
        # query pages again
        pages = notionapi.query_pages(query_url, apiimport.DATABASE_ID, query_payload, headers)

        # Traverse queried pages
        titles = datahandling.retrieveInfo(pages)

        # Monthly database exists now

    else:
        print("Yep - monthly page exists.")


        

    # Obtain data from diary template?
    diary_results_tmp = datahandling.json_open("page_template/diary.json")
    diary_results = [diary_results_tmp[0]]
    #print(diary_results)

    retrieve_id = titles[today_folder][1].replace("-","")

    retrieve_url = f"https://api.notion.com/v1/databases/{retrieve_id}/query"

    pages = notionapi.query_pages(retrieve_url, retrieve_id, query_payload, headers)

    titles = datahandling.retrieveInfo(pages)
    

    gcal_events = gcalapi.gcal_access()
    #print(gcal_events)

    events_dict = {}

    for eventName in gcal_events.keys():
        #print(eventName, gcal_events[eventName][0], gcal_events[eventName][1])
        for i in range(gcal_events[eventName][0], gcal_events[eventName][1] + 1):
            if(i >= 9 and i < 12):
                events_dict["{}AM".format(i)] = events_dict.get("{}AM".format(i),"") + eventName
            if(i == 12):
                events_dict["12PM"]= events_dict.get("12PM","") + eventName
            if(i > 12 and i < 24):
                events_dict["{}PM".format(i-12)] = events_dict.get("{}PM".format(i-12),"") + eventName
            if(i == 24):
                events_dict["12AM+1"] = events_dict.get("12AM+1","") + eventName

    print(events_dict)


    if today_diary_name not in titles.keys():

        print("Nope - daily diary doesn't exist. Searching this month's folder for syncing data...")

        # Search the latest diary in same month (hopefully yesterday)
        if(len(to_do_backup) == 0):
            queryday = now

            while queryday != queryday.replace(day=1):
                queryday -= timedelta(days=1)
                queryday_diary_name = queryday.strftime("%B %d (%a)")
                print(queryday_diary_name)
                # perform query
                if queryday_diary_name in titles.keys():
                    print("target diary found")
                    # query content of the diary
                    target_diary_id = titles[queryday_diary_name][1].replace("-","")
                    target_diary_url = f"https://api.notion.com/v1/blocks/{target_diary_id}/children"
                    target_diary_data = notionapi.get_data(target_diary_url, headers)
                    for datalet in target_diary_data:
                        #print(datalet)
                        if 'to_do' in datalet.keys():
                            datalet['to_do']['checked'] = False
                            if datalet['has_children'] == True:
                                target_child_id = datalet['id'].replace("-","")
                                target_child_url = f"https://api.notion.com/v1/blocks/{target_child_id}/children"
                                target_child_data = notionapi.get_data(target_child_url, headers)

                                children_data = []
                                for it in range(len(target_child_data)):
                                    interim_data = {}
                                    interim_data['type'] = target_child_data[it]['type']

                                    if target_child_data[it]['type'] == 'image':
                                        continue

                                    interim_data[interim_data['type']] = target_child_data[it][interim_data['type']]

                                    if target_child_data[it]['type'] == 'to_do':
                                        interim_data[interim_data['type']]['checked'] = False
                                    
                                    children_data.append(interim_data)

                                datalet['to_do']['children'] = children_data
                                
                            # Gotta deal with children
                            to_do_backup.append(datalet)

                    break
            
        
        #print(to_do_backup)

        print("Creating today's diary - " + today_diary_name)

        create_payload = notionapi.empty_page_format(retrieve_id, today_diary_name, "📅")

        create_url = "https://api.notion.com/v1/pages"

        notionapi.create_pages(create_url, create_payload, headers)

        # Refresh information
        pages = notionapi.query_pages(retrieve_url, retrieve_id, query_payload, headers)

        titles = datahandling.retrieveInfo(pages)

        # Update page content

        update_id = titles[today_diary_name][1].replace("-","")

        update_url = f"https://api.notion.com/v1/blocks/{update_id}/children"

        # Create Table
        diary_results.extend(to_do_backup)
        diary_results.extend(diary_results_tmp[1:])
        
        

        for i in range(0,len(diary_results)):
            if diary_results[i]["type"] == "to_do":
                ()
            if diary_results[i]["type"] == "table":
                diary_results[i] = {  "type": "table",
                "table": {
                    "table_width": 3,
                    "children":[
                        {"type":"table_row","table_row":{"cells":[[{"type":"text","text":{"content":"Timeframe"},"annotations":{"bold":True}}],\
                                                                                        [{"type":"text","text":{"content":"Tasks"},"annotations":{"bold":True}}],\
                                                                                            [{"type":"text","text":{"content":"Details"},"annotations":{"bold":True}}]]}}]
                    }
                }
                for a in range(8,12):
                    diary_results[i]["table"]["children"].append({"type":"table_row","table_row":{"cells":[[{"type":"text","text":{"content":f"{a}AM"}}],[{"type":"text","text":{"content":events_dict.get("{}AM".format(a),"")}}],[]]}})
                diary_results[i]["table"]["children"].append({"type":"table_row","table_row":{"cells":[[{"type":"text","text":{"content":"12PM"}}],[{"type":"text","text":{"content":events_dict.get("12PM","")}}],[]]}})
                for a in range(1,12):
                    diary_results[i]["table"]["children"].append({"type":"table_row","table_row":{"cells":[[{"type":"text","text":{"content":f"{a}PM"}}],[{"type":"text","text":{"content":events_dict.get("{}PM".format(a),"")}}],[]]}})
                diary_results[i]["table"]["children"].append({"type":"table_row","table_row":{"cells":[[{"type":"text","text":{"content":"12AM+1"}}],[{"type":"text","text":{"content":events_dict.get("12AM+1","")}}],[]]}})

        update_payload = {
            "children": diary_results
        }
        
        #print(update_payload)

        response = requests.patch(update_url, headers=headers, json=update_payload)
        print(response)

        
        
    else:
        print("Yep - daily diary exists")


if __name__ == '__main__':
    main()
