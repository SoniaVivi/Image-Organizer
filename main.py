from PIL import Image
import os
import imagehash

def get_files(path, arg):
  with os.scandir(path) as dirs:
    for entry in dirs:
      if entry.is_file():
        arg(entry)
      elif entry.is_dir():
        get_files(os.path.join(path, entry.name), arg)

fin = lambda x: print(x.name, x.path, imagehash.phash(Image.open(x.path)))
get_files('assets', fin)
