import requests
import json


def req(f_url, f_query):
    url = f_url
    querystring = f_query

    headers = {
        'x-rapidapi-key': "545765e222mshcffb1b8429ecff6p165b8ajsn4627ab9217ae",
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
