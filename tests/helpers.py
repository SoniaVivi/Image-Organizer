import sqlite3
from vivid.filesearch import get_files

IMG_PATH = 'tests/test_images/'

def file_exists(name, path=IMG_PATH):
  for f in get_files(path):
    if name == f.name:
      return True
  return False
