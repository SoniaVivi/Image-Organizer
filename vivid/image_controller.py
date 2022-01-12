import os
import imagehash
from PIL import Image
from .database_add import RecordAdd
from .filesearch import get_files
from .database_controller import DatabaseController
from .blacklist import Blacklist
from os.path import isdir, isfile, exists
from pathlib import Path
from .config import Config
import random, string


class ImageController():
  blacklist = Blacklist()
  logging = Config().read('image_controller', 'logging')

  def __init__(self, db=None, test=False, **kwargs):
    self.table_name = 'Image'
    self._create_thumbnails_path(test)
    self.db = db if db else DatabaseController(test)
    self.use_blacklist = kwargs.get('use_blacklist', True)
    self._retrieve_blacklisted()

  def add(self, path, **kwargs):
    if isdir(path):
      self.add_directory(path, False, **kwargs)
    elif isfile(path):
      self.add_image(path, **kwargs)
    return self

  def add_image(self, path, **kwargs):
    img_hash = self.get_hash(path)
    blacklist_check = kwargs.get('blacklist_check', True)

    if blacklist_check:
      if self.is_blacklisted((img_hash, 'hash')) or\
        self.is_blacklisted((path, 'path')):
        if ImageController.logging == 'True':
          print(f"Skipping {path} | Reason: Blacklisted path or directory ancestor")
        return self
    if not self._is_valid(path, img_hash, **kwargs):
      if ImageController.logging == 'True':
        print(f"Skipping {path} | Reason: Image is invalid or already exists")
      return self

    name = self._generate_name(path, img_hash, **kwargs)

    record_add = RecordAdd()
    attribute_pairs = [
                       ('path', path),
                       ('name', name ),
                       ('hash', img_hash)
                      ]

    for func in dir(record_add):
      if func[0] != '_' and func != 'db_connection' and callable(getattr(record_add, func)):
        attribute_pairs.append(getattr(record_add, func)(path))
    record_id = self.db.create(
      self.table_name, dict(zip(list(map(lambda x: x[0], attribute_pairs)),
                                list(map(lambda x: x[1], attribute_pairs)))))
    self._create_thumbnail(path, record_id)
    if ImageController.logging == 'True':
      print(f"Added {path}")
    return self

  def add_directory(self, path, toplevel_only=True, **kwargs):
    if self.is_blacklisted((path, 'directory')):
      return self
    for file in get_files(path, toplevel_only):
      self.add_image(file.path, **kwargs)
    return self

  def remove(self, path, **kwargs):
    self._remove_thumbnail(path)
    should_blacklist = kwargs.get('blacklist', False)
    image_data = self.db.find_by('Image', {'path': path})
    self.db.delete('Image', ('path', path))

    if should_blacklist == 'hash' or should_blacklist == 'all':
      self.blacklist_image(image_data['hash'], 'hash')
    if should_blacklist == 'path' or should_blacklist == 'all':
      self.blacklist_image(image_data['path'], 'path')

    if kwargs.get('db_only', True):
      return self
    if os.path.exists(path):
      os.remove(path)
    return self

  def blacklist_image(self, textable, textable_type):
    if self.db.exists('ImageBlacklist', {'textable': textable}):
      return self
    self.db.create('ImageBlacklist',
                              {'textable': textable,
                               'textable_type': textable_type})
    return self

  def blacklist_directory(self, path):
    if self.db.exists('ImageBlacklist', {'textable': path}):
      return self
    self.db.create('ImageBlackList',
                              {'textable': path, 'textable_type': 'directory'})
    ImageController.blacklist.add(path)

  def get_hash(self, path):
    try:
      h = imagehash.phash(Image.open(path))
    except Exception as e:
      print(e)
    else:
      return str(h)

  def get_thumbnail(self, image_id):
    return f"{self.thumbnails_path}{image_id}.png"

  def rename(self, path, new_name, on_disk=True, in_db=True):
    img_data = self.db.find_by('Image', ('path', path,))
    img_path = ['path', path]

    if on_disk:
      new_path = \
                f"{os.path.split(path)[0]}/{new_name}.{img_data['image_type']}"

      if os.path.exists(new_path):
        return img_path

      img_path[1] = new_path
      os.rename(path, img_path[1])
      self.db.update('Image', img_data['id'], (img_path,))

    if in_db:
      self.db.update('Image', img_data['id'], (('name', new_name,),))

    return tuple(img_path)

  def existance_check(self):
    for image in self.db.between('Image',
                                  self.db.get_first('Image')['id'],
                                  self.db.get_last('Image')['id']):
      path = image['path']
      if not exists(path):
        self.remove(path, db_only=True)

  def is_blacklisted(self, data=()):
    if not self.use_blacklist:
      return False

    (textable, textable_type) = data
    if textable_type == 'path' or textable_type == 'directory':
      if ImageController.blacklist.exists(textable):
        return True
      if textable_type == 'directory':
        return False

    return not not self.db.find_by('ImageBlacklist',
                                              {'textable': textable,
                                              'textable_type': textable_type})

  def _create_thumbnail(self, path, image_id):
    with Image.open(path) as img:
      img.thumbnail((250, 125,))
      img.save(
        Path(f"{self.thumbnails_path + str(image_id)}.png"), format="PNG")

  def _retrieve_blacklisted(self):
    if not self.use_blacklist:
      return

    sql = f"SELECT textable AS directories\
            FROM ImageBlacklist\
            WHERE textable_type='directory'"
    for x in self.db.execute(sql).fetchall():
      ImageController.blacklist.add(x[0])

  def _remove_thumbnail(self, path):
    data = self.db.find_by('Image', ('path', path))
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

  def _is_valid(self, path, img_hash, **kwargs):
    if not img_hash or \
       self.db.exists('Image', ('path', path)) or\
       (kwargs.get('unique', False) and\
          self.db.exists('Image', ('hash', img_hash))):
      return False
    return True

  def _generate_name(self, path, img_hash, **kwargs):
    if kwargs.get('scramble_name', False):
      return self._random_string(32)
    elif kwargs.get('hash_as_name', False):
      return img_hash
    return os.path.splitext(os.path.basename(path))[0]

  def _random_string(self, length):
   return ''.join(random.choice(string.ascii_lowercase) for i in range(length))
