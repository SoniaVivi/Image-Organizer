import os
import fleep


class RecordAdd:
    def get_image_type(self, path):
        with open(path, "rb") as file:
            info = fleep.get(file.read(128))
        if len(info.type) != 0 and info.type[0].find("image") != -1:
            return ("image_type", info.extension[0])
        else:
            return ("image_type", "")
