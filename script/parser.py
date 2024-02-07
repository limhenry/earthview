# Sayan Goswami (c) 6 July 2016
import concurrent.futures
import urllib.request
from json import dumps
from bs4 import BeautifulSoup

result = []
file = open('earthview.json','a')

URLS = ['https://earthview.withgoogle.com/' + str(x) for x in range(1000,7030)]

# Retrieve a single page and report the URL and contents
def load_url(url, timeout):
    with urllib.request.urlopen(url, timeout=timeout) as conn:
        data =  conn.read()
        html = BeautifulSoup(data,"html.parser")
        Region = str((html.find("div", class_="content__location__region")).text)
        Country = str((html.find("div", class_="content__location__country")).text)
        Everything = html.find("a", id="globe", href=True)
        GMapsURL = Everything['href']
        Image = 'https://www.gstatic.com/prettyearth/assets/full/' + str(url.split('/')[-1]) + '.jpg'
        a = {'region': Region, 'country': Country, 'map': GMapsURL, 'image': Image}
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
            pass
        else:
            # Do ya thing
            result.append(res)
            print("Fetched -> | " + str(url.split('/')[-1]) + " | ")


final_file = dumps(result,indent=4) #Dump the json file finally
file.write(final_file)
file.close()