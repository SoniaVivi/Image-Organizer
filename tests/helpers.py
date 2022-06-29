import sqlite3
from vivid.filesearch import get_files
from pathlib import Path

CURRENT_PATH = str(Path().absolute())

IMG_PATH = CURRENT_PATH + "/tests/test_images/"

THUMBNAIL_PATH = CURRENT_PATH + "/tests/thumbnails"


def file_exists(name, path=IMG_PATH):
    for f in get_files(path):
        if name == f.name:
            return True
    return False
