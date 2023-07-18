import concurrent.futures
import requests
from heapq import merge
import re
import json
from bs4 import BeautifulSoup

base_url = "https://earthview.withgoogle.com/"

"""Helper class for parsing and sorting images and their locations"""
class Location:
    def __init__(self, id: int, resp: requests.Response) -> None:
        # the id is the page index at earthview
        self.id = id
        html = BeautifulSoup(resp.content.decode('utf-8'))
        body = str(html.body)
        # some pages have different quot encodings than others
        body = body.replace("&quot;", '"')
        # photo data is a json object inside of the body block
        data_regex = re.compile("data-photo=['\"]{.*}[\"']")
        results = data_regex.search(body)
        assert results != None, f"could not parse data for id: {self.id}"
        try:
            # turn to json remove photo-data=' and closing quote
            self.photo_data = json.loads(results.group(0)[12:-1])
        except ValueError:
            assert False, f"Invalid json for id: {self.id}"
        assert self.photo_data["photoUrl"] != None

    def get_photo_data(self):
        return self.photo_data

    def __lt__(self, obj):
        return self.id < obj.id

    def __gt__(self, obj):
        return self.id > obj.id
    
    def le(self, obj):
        return self.id <= obj.id
    
    def ge(self, obj):
        return self.id >= obj.id
    
    def __eq__(self, obj):
        return self.id == obj.id
    
    def __repr__(self) -> str:
        return str(self.id)

    def __str__(self) -> str:
        return str(self.id)

    


def discover_range(start: int, end: int) -> list[Location]:
    """discovers valid photo indeces in the given range"""
    locations = []
    for i in range(start, end):
        url = base_url+str(i)
        resp = requests.get(url)
        # There are holes in Google's earthview, check for 200 status code
        if resp.status_code == 200:
            locations.append(Location(i, resp))
    return locations

def print_locations_to_file(locations: list[Location], filepath: str):
    """Writes the locations to a given file as a json list"""
    res = open(filepath, "wb")
    res.write(str.encode("["))
    last_loc = locations.pop()
    for loc in locations:
        loc_data = json.dumps(loc.get_photo_data(), ensure_ascii=False).encode('utf8')
        res.write(loc_data)
        res.write(str.encode(",\n"))
    loc_data = json.dumps(last_loc.get_photo_data(), ensure_ascii=False).encode('utf8')
    res.write(loc_data)
    res.write(str.encode("\n]"))
    res.close()




def collect_all_locations() -> list[Location]:
    """Collects all valid image locations from earthview. Uses 200 workers, each one processing 20 possible images"""
    all_locations = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executer:
        futures = []
        base = 1000
        i = 0
        start = base + (20*i)
        end = base + ((20*(i+1))-1)
        while end < 7030:
            futures.append(executer.submit(discover_range, start=start, end=end))
            i += 1
            start = base + (20*i)
            end = base + ((20*(i+1))-1)
        for future in concurrent.futures.as_completed(futures):
            # Each future to complete returns a sorted list, use merge sort to keep list sorted
            all_locations = list(merge(all_locations, future.result()))
    return all_locations
