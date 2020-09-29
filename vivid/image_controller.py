import os
import imagehash
from PIL import Image
from .database_add import RecordAdd
from .filesearch import get_files
from .database_controller import DatabaseController

class ImageController():
  def __init__(self, db_controller=None, test=False):
    self.table_name = 'Image'
    if db_controller:
      self.db_controller = db_controller
    else:
      self.db_controller = DatabaseController(test)

  def add_image(self, path, unique=False):
    img_hash = self.get_hash(path)
    if not img_hash or \
       self.db_controller.exists('Image', ('path', path)) or \
       (unique and self.db_controller.exists('Image', ('hash', img_hash))):
      return
    record_add = RecordAdd(self.table_name)
    attribute_pairs = [
                       ('path', path),
                       ('name', os.path.splitext(os.path.basename(path))[0]),
                       ('hash', img_hash)
                      ]

    for func in dir(record_add):
      if func[0] != '_' and func != 'db_connection' and callable(getattr(record_add, func)):
        attribute_pairs.append(getattr(record_add, func)(path))
    self.db_controller.create(
                              self.table_name,
                              dict(zip(list(map(lambda x: x[0], attribute_pairs)),
                                    list(map(lambda x: x[1], attribute_pairs))))
                            )

  def add_directory(self, path, toplevel_only=True, unique=False):
    for file in get_files(path, toplevel_only):
      self.add_image(file.path, unique)

  def remove(self, path, db_only=True):
    self.db_controller.delete('Image', ('path', path))
    if db_only:
      return
    os.remove(path)


  def get_hash(self, path):
    try:
      h = imagehash.phash(Image.open(path))
    except Exception as e:
      print(e)
    else:
      return str(h)

  def get_thumbnail(self, path):
    pass

  def rename(self, path, new_name):
    extension = self.db_controller.find_by('Image', ('path', path))['image_type']
    new_path = "{}/{}.{}".format(os.path.split(path)[0],
                                 new_name,
                                 extension)
    os.rename(path, new_path)
    self.remove(path)
    self.add_image(new_path)
    return new_path

