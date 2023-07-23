import json
import requests
import os

NEXT_IMAGE_POINTER_KEY = "earthview_pointer"
LOCAL_IMAGES_KEY = "local_paths"
DOWNLOAD_PATH_KEY = "download_path"
class Image_Library():
    def __init__(self, library_config_path: str, image_data_file_path: str) -> None:
        config_file_handler = open(library_config_path)
        self.config = json.load(config_file_handler)
        config_file_handler.close()

        image_data_handler = open(image_data_file_path, encoding="utf-8")
        self.image_data = json.load(image_data_handler)
        image_data_handler.close()

        self.download_path = self.config[DOWNLOAD_PATH_KEY]
        self.next_image = self.config[NEXT_IMAGE_POINTER_KEY]


    def next(self) -> str:
        # TODO: make network and io operations async
        # download next image
        # remove current image
        # return local image path
        self.download_image(self.next_image)
        bg = self.image_data[self.next_image]
        # bg_loc = self.image_data[self.next_image]["local_path"]
        self.next_image += 1
        return bg["local_path"]

    def download_image(self, index: int):
        img_bytes = requests.get(self.image_data[index]["photoUrl"]).content
        img_name = self.image_data[index]["name"].strip()+".jpg"
        img_path = os.path.join(self.download_path, img_name)
        with open(img_path, 'wb') as handler:
            handler.write(img_bytes)
        self.image_data[index]["local_path"]= img_path

