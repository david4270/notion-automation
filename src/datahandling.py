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
