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

def get_data(blkID, header):
    blk_url = f"https://api.notion.com/v1/blocks/{blkID}/children"
    blk_response = requests.get(blk_url, headers = header)
    blk_data = blk_response.json()
    """
    with open(f'db_{blkID}.json', 'w', encoding='utf8') as f:
        json.dump(blk_data, f, ensure_ascii=False, indent = 4)
    """
    blk_results = blk_data["results"]
    return blk_results