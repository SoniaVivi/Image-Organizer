from .record import Record
from PIL import Image
import os
import imagehash
import fleep
import sqlite3

class ImageRecord(Record):

  table = ('Image',)

  def __init__(self, attributes=None, **kwargs):
    super().__init__(self.table[0], attributes)

  def rename(self, new_name, disk=True):
    new_path = "{}/{}.{}".format(os.path.split(self.attributes['path'])[0],
                                 new_name,
                                 self.attributes['extension'])
    os.rename(self.attributes['path'], new_path)
    self.attributes['name'], self.attributes['path'] = new_name, new_path
    self.save()

  def delete(self, on_disk=False):
    if on_disk:
      os.remove(self.attributes['path'])
    super().delete()


  @staticmethod
  def from_path(path, unique=False):
    record = ImageRecord({})
    try:
      record.attributes = {'name': os.path.splitext(os.path.basename(path))[0],
                           'path': path, 'hash': ImageRecord.get_hash(path),
                           'extension': ImageRecord.get_image_type(path)}
    except Exception as e:
      print(e)
    else:
      if record.attributes['hash'] != None:
        if unique and Record.find_by(['hash', record.attributes['hash']], 'Image'):
          return
        return record.create()

  @staticmethod
  def get_image_type(path):
    with open(path, 'rb') as file:
      info = fleep.get(file.read(128))
    if len(info.type) != 0 and info.type[0].find('image') != -1:
      return info.extension[0]
    else:
      return False

  @staticmethod
  def get_hash(path):
    try:
      h = imagehash.phash(Image.open(path))
    except Exception as e:
      print(e)
    else:
      return str(h)
