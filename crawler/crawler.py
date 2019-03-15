import requests

APIKEY = "52e15631e9c84d7890a7bff514a4138b" # News API' s key
FOLDERROOT = "./log/"

def main():
    ##### Initialize the request parameters
    endpoint = "everything"
    domains  = "nytimes.com"
    language = "en"
    page = 1
    request_get = generate_request_string(endpoint,domains, language, page)
    r = requests.get(request_get)

    filename = FOLDERROOT + domains[0:-4] + "_page_" + str(page) + '.txt'
    Write_into_File(filename,r)

    totalResults = r.json()['totalResults']
    request_iteration = int(totalResults/20)
    print('log into ' + filename)
    ## The web request can only return up to 20 results, so use the page patameter in your request to page through them
    for target_page in range(2,request_iteration+1,1):
        page = target_page
        request_get = generate_request_string(endpoint,domains, language, page)
        r = requests.get(request_get)
        filename = FOLDERROOT + domains[0:-4] + "_page_" + str(page) + '.txt'
        Write_into_File(filename, r)
        print('log into ' + filename)

    #r = Read_from_File(filename)
    #print (r)

def generate_request_string(endpoint,domains, language, page):
    request_string = "https://newsapi.org/v2/" + endpoint + "?domains=" + \
        domains + "&language=" + language + \
        "&page=" + str(page) + "&apiKey=" + APIKEY
    return request_string

def Write_into_File(filename,r):
    chunk_size = 100
    #write into file
    with open(filename, 'wb') as fwrite:
        for chunk in r.iter_content(chunk_size):
           fwrite.write(chunk)
        fwrite.close()
        return

def Read_from_File(filename):
    #read from file
    with open(filename) as fread:
        import json
        data = json.load(fread)
        print (data)
        return data

if __name__ == "__main__":
    main()
