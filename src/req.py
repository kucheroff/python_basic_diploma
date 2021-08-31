import requests
import json


def req(f_url, f_query):
    url = f_url
    querystring = f_query

    headers = {
        'x-rapidapi-key': "e1b6c495d9msh331ef30bb042c1dp12c685jsn6a5c1b2e7f1b",
        'x-rapidapi-host': "hotels4.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    print(response.status_code)
    if response.status_code == 200:
        data = json.loads(response.text)
        print(data)
        return data
    else:
        return None
