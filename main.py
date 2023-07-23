import os.path
import json
import ctypes
from image_library import Image_Library
from earthview_scraper import earthview_scraper


CONFIG_PATH = "config.json"

EATHVIEW_DATA_PATH_KEY = "earthview_data_path"
EARTHVIEW_CONFIG_PATH = "earthview_config_path"

class BackgroundManager():
    def __init__(self) -> None:
        self.config_path = CONFIG_PATH
        config_file_handler = open(self.config_path)
        self.config = json.load(config_file_handler)
        config_file_handler.close()
        self.earthview_data_path = self.config[EATHVIEW_DATA_PATH_KEY]
        self.earthveiw_config_path = self.config[EARTHVIEW_CONFIG_PATH]

        if not os.path.isfile(self.earthview_data_path):
            print("Earthview data is missing")
            print("Collecting Earthview data")
            locations = earthview_scraper.collect_all_locations()
            earthview_scraper.print_locations_to_file(locations, self.earthview_data_path)
        else:
            print("Earthview data is present")
        earthview_lib = Image_Library(self.earthveiw_config_path, self.earthview_data_path)
        background_loc = earthview_lib.next()
        ctypes.windll.user32.SystemParametersInfoW(20, 0, background_loc , 0)

        



def main():
    bm = BackgroundManager()

if __name__ == "__main__":
    main()
