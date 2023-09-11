import requests
import json

def query_pages(url, dbid, payload, header):
    response = requests.post(url, json = payload, headers = header)

    data = response.json()
    """
    with open(f'db_{dbid}.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent = 4)
    """
    results = data["results"]
    return results

def create_pages(url, payload, header):
    response = requests.post(url, json = payload, headers = header)
    """
    data = response.json()

    with open('create.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent = 4)
    """
    return response

def get_data(url, header):
    
    response = requests.get(url, headers = header)
    data = response.json()
    """
    with open(f'db_{blkID}.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent = 4)
    """
    results = data["results"]
    return results

def empty_database_format(parent_db_id, name):
    empty_database = {
        "parent": {
            "type": "database_id",
            "database_id": parent_db_id
        },
        "title": [
            {
                "type": "text",
                "text": {
                    "content": name,
                },
                "plain_text": name
            }
        ],
        "properties": {
            "Last edited time": {
                "name": "Last edited time",
                "type": "last_edited_time",
                "last_edited_time": {}
            },
            "Created by": {
                "name": "Created by",
                "type": "created_by",
                "created_by": {}
            },
            "Created time": {
                "name": "Created time",
                "type": "created_time",
                "created_time": {}
            },
            "Status": {
                "name": "Status",
                "type": "select",
                "select": {
                    "options": []
                }
            },
            "Page": {
                "id": "title",
                "name": "Page",
                "type": "title",
                "title": {}
            }
        }


    }
    return empty_database

def empty_page_format(parent_db_id, name, page_emoji):
    empty_page = {
            "parent": {
                "type": "database_id",
                "database_id": parent_db_id
            },
            "icon": {
                "type": "emoji",
                "emoji": page_emoji
            },
            "properties": {
                "Page": {
                    "id": "title",
                    "type": "title",
                    "title": [
                        {
                            "type": "text",
                            "text": {
                                "content": name
                            },
                            "plain_text": name
                        }
                    ]
                }         
            }
        }
    return empty_page

def set_children(data, headers):
    if data['has_children'] == True:
        target_child_id = data['id'].replace("-","")
        target_child_url = f"https://api.notion.com/v1/blocks/{target_child_id}/children"
        target_child_data = get_data(target_child_url, headers)

        children_data = []
        for datalet in target_child_data:
            interim_data = {}

            # notion API does not support more than 2-level nested children
            #set_children(datalet, headers)

            interim_data['type'] = datalet['type']

            if datalet['type'] == 'image':
                continue

            interim_data[interim_data['type']] = datalet[interim_data['type']]

            if datalet['type'] == 'to_do':
                interim_data[interim_data['type']]['checked'] = False

            children_data.append(interim_data)
        
        #print(len(children_data))

        data[data['type']]['children'] = children_data

        #print(data)
        #print("\n")
    #return data