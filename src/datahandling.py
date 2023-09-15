import json
import re
from collections import defaultdict

import datetime
from dateutil.tz import *

import src.notionapi as notionapi
import src.gcalapi as gcalapi

def retrieveInfo(pages):
    # Traverse queried pages
    titles = {}
    for page in pages:
    
        url = page["url"]
        objType = page["object"]
        id = page["id"]

        if objType == "page":
            title = page["properties"]["Page"]["title"][0]["plain_text"]
        elif objType == "database":
            title = page["title"][0]["plain_text"]
        
        #print(url, objType, id, title)

        titles[title] = (objType, id)
    
    return titles

def json_open(fileName):
    data = {}
    with open(fileName,'r',encoding='utf8') as f:
        data = json.load(f)
    
    f.close()
    return data["results"]

def targetDiaryHandling(queryday, queryday_diary_name, to_do_backup, titles, headers):
        
        # query content of the diary
        target_diary_id = titles[queryday_diary_name][1].replace("-","")
        target_diary_url = f"https://api.notion.com/v1/blocks/{target_diary_id}/children"
        target_diary_data = notionapi.get_data(target_diary_url, headers)
        target_event_list = defaultdict(list)
        for datalet in target_diary_data:
            #print(datalet)
            if 'table' in datalet.keys():
                if datalet['has_children']:
                    target_child_id = datalet['id'].replace("-","")
                    target_child_url = f"https://api.notion.com/v1/blocks/{target_child_id}/children"
                    target_child_data = notionapi.get_data(target_child_url, headers)
                    for childlet in target_child_data[1:]:
                        if len(childlet['table_row']['cells'][1]) != 0:
                            eventlistathr = childlet['table_row']['cells'][1][0]['text']['content'].split(',')
                            if eventlistathr[-1] == '':
                                eventlistathr = eventlistathr[:-1]
                            for eventhr in eventlistathr:
                                timeset = re.findall('\d+',childlet['table_row']['cells'][0][0]['text']['content'])
                                target_event_list[eventhr].append(int(timeset[0])*100 + int(timeset[1]))
                        #print()
            if 'to_do' in datalet.keys():
                datalet['to_do']['checked'] = False
                notionapi.set_children(datalet,headers)
                    
                # Gotta deal with children
                to_do_backup.append(datalet)
        
        queryday_events_dict = retrieveEvents(queryday)

        #print(queryday_events_dict, target_event_list)

        for hr in queryday_events_dict.keys():
            #hr_abbr = hr[0:2]
            hr_abbr = hr[0:2] + hr[3:5]
            #print(hr[0:2])
            #print(hr[0:2] + hr[3:5])
            for ev in queryday_events_dict[hr]:
                if ev in target_event_list.keys():
                    #print(target_event_list[ev])

                    for hr_abbr in target_event_list[ev]:
                        target_event_list[ev].remove(hr_abbr)
                    
                    target_event_list.pop(ev)
                    
        #print(target_event_list)

        gcalapi.gcal_event(queryday,target_event_list)

def retrieveEvents(day):
    gcal_events = gcalapi.gcal_access(day)
    events_dict = defaultdict(list)
    
    for eventName in gcal_events.keys():
        #print(eventName, gcal_events[eventName][0], gcal_events[eventName][1])
        for i in range(max(8,gcal_events[eventName][0]//100), min(24,gcal_events[eventName][1]//100 + 1)):
            if gcal_events[eventName][0] % 100 == 0 or i > gcal_events[eventName][0]//100:
                events_dict["{}:00".format(i)].append(eventName)
            if gcal_events[eventName][1] % 100 != 0 or i < gcal_events[eventName][1]//100:
                events_dict["{}:30".format(i)].append(eventName)
    #print(events_dict)
    return events_dict

#retrieveEvents(datetime.datetime.now(tzlocal()))