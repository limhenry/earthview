# Sayan Goswami (c) 6 July 2016
# Modified by Alex Persian 7 Feb 2024
import concurrent.futures
import urllib.request
import json

result = []
file = open('earthview.json','a')

pid = open('photo_ids.json')
photo_ids = json.load(pid)
URLS = ['https://www.gstatic.com/prettyearth/assets/data/v3/' + str(x) + '.json' for x in photo_ids]

# Retrieve a single json response and format the contents
def load_url(url, timeout):
    headers = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36' }
    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req, timeout=timeout) as conn:
        data = json.load(conn)

        id = data.get('id', '')

        lat = data.get('lat', '')
        lng = data.get('lng', '')
        zoom = data.get('zoom', '')

        if 'geocode' in data:
            geocode = data.get('geocode', '')
            country = geocode.get('country', '')
            region = geocode.get('region', '')
        else:
            country = data.get('country', '')
            region = data.get('region', '')

        attribution = data.get('attribution', '')

        image = 'https://www.gstatic.com/prettyearth/assets/full/' + str(id) + ".jpg"
        gmapsURL = 'https://www.google.com/maps/@' + str(lat) + ',' + str(lng) + ',' + str(zoom) + 'z/data=!3m1!1e3'

        a = {'id': id, 'region': region, 'country': country, 'map': gmapsURL, 'image': image, 'attribution': attribution}
        return a

# We can use a with statement to ensure threads are cleaned up promptly
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    # Start the load operations and mark each future with its URL
    future_to_url = {executor.submit(load_url, url, 60): url for url in URLS}
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            res = future.result()
        except Exception as exc:
            print("Failed: " + str(url.split('/')[-1]) + " -> " + str(exc))
            pass
        else:
            # Do ya thing
            result.append(res)
            print("Fetched -> | " + str(url.split('/')[-1]) + " | ")

def sort_by_id(e):
    return e['id']
result.sort(key=sort_by_id)

final_file = json.dumps(result,indent=2) #Dump the json file finally
file.write(final_file)
file.close()
