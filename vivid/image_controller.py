import os
import imagehash
from PIL import Image
from .database_add import RecordAdd
from .filesearch import get_files
from .database_controller import DatabaseController
from os.path import isdir, isfile
from pathlib import Path


class ImageController():
  def __init__(self, db=None, test=False):
    self.table_name = 'Image'
    self._create_thumbnails_path(test)
    self.db_controller = db if db else DatabaseController(test)

  def add(self, path):
    if isdir(path):
      self.add_directory(path, False)
    elif isfile(path):
      self.add_image(path)
    return self

  def add_image(self, path, unique=False):
    img_hash = self.get_hash(path)
    if not img_hash or \
       self.db_controller.exists('Image', ('path', path)) or \
       (unique and self.db_controller.exists('Image', ('hash', img_hash))):
      return self
    record_add = RecordAdd()
    attribute_pairs = [
                       ('path', path),
                       ('name', os.path.splitext(os.path.basename(path))[0]),
                       ('hash', img_hash)
                      ]

    for func in dir(record_add):
      if func[0] != '_' and func != 'db_connection' and callable(getattr(record_add, func)):
        attribute_pairs.append(getattr(record_add, func)(path))
    record_id = self.db_controller.create(
      self.table_name, dict(zip(list(map(lambda x: x[0], attribute_pairs)),
                                list(map(lambda x: x[1], attribute_pairs)))))
    self._create_thumbnail(path, record_id)
    return self


  def add_directory(self, path, toplevel_only=True, unique=False):
    for file in get_files(path, toplevel_only):
      self.add_image(file.path, unique)
    return self

  def remove(self, path, db_only=True):
    self._remove_thumbnail(path)
    self.db_controller.delete('Image', ('path', path))

    if db_only:
      return self
    if os.path.exists(path):
      os.remove(path)
    return self

  def get_hash(self, path):
    try:
      h = imagehash.phash(Image.open(path))
    except Exception as e:
      print(e)
    else:
      return str(h)

  def get_thumbnail(self, image_id):
    return f"{self.thumbnails_path}{image_id}.png"

  def _create_thumbnail(self, path, image_id):
    with Image.open(path) as img:
      img.thumbnail((250, 125,))
      img.save(
        Path(f"{self.thumbnails_path + str(image_id)}.png"), format="PNG")

  def _remove_thumbnail(self, path):
    data = self.db_controller.find_by('Image', ('path', path))
    if not data:
      return
    img_id = data['id']
    thumbnail_path  = f"{self.thumbnails_path + str(img_id)}.png"
    if isfile(thumbnail_path):
      os.remove(thumbnail_path)

  def _create_thumbnails_path(self, test):
    self.thumbnails_path = './tests/thumbnails' if test else './thumbnails'
    if not isdir(self.thumbnails_path):
      os.mkdir(self.thumbnails_path)
    self.thumbnails_path += '/'

  def rename(self, path, new_name, on_disk=True, in_db=True):
    img_data = self.db_controller.find_by('Image', ('path', path,))
    img_path = ['path', path]

    if on_disk:
      new_path = \
                f"{os.path.split(path)[0]}/{new_name}.{img_data['image_type']}"

      if os.path.exists(new_path):
        return img_path

      img_path[1] = new_path
      os.rename(path, img_path[1])
      self.db_controller.update('Image', img_data['id'], (img_path,))

    if in_db:
      self.db_controller.update('Image', img_data['id'], (('name', new_name,),))

    return tuple(img_path)

