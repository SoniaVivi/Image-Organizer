from vivid import record
from vivid.image_record import ImageRecord
from .helpers import IMG_PATH, count_rows, file_exists
from vivid import filesearch as fs
import sqlite3
import os
from shutil import copyfile

def setup_record():
  record.Record.conn = record.setup_database(True)
  return ImageRecord()

class TestImageRecord:

  img = setup_record()

  def test_image_type(self):
    assert ([ImageRecord.get_image_type(f.path) != False for\
            f in fs.get_directory_family(IMG_PATH)] ==
            [False, True, False, False, True, True, True, True])

  def test_get_hash(self):
    assert ImageRecord.get_hash(IMG_PATH + 'cat1.jpg') == 'e3169ce9d046ad9c'

  def test_from_path(self):
    self._reset_table()
    record = ImageRecord.from_path(IMG_PATH + 'cat1.jpg')
    assert record.attributes == {'id': 1, 'name': 'cat1',
                                 'path': IMG_PATH + 'cat1.jpg',
                                 'hash': 'e3169ce9d046ad9c',
                                 'extension': 'jpg'}
    assert self.img.conn.execute('''SELECT count(*) FROM Image''').fetchone()\
                                                                       == (1,)

  def test_columns(self):
    assert ImageRecord.get_columns('Dog') == None
    assert self.img.columns() == ['id', 'name', 'path', 'hash', 'extension']

  def test_delete(self):
    record = ImageRecord.find_by(['id', 1])
    row_count = count_rows(self.img.conn, 'Image')
    record.delete()
    assert row_count > count_rows(self.img.conn, 'Image')

  def test_rename(self):
    self._reset_table()
    img = ImageRecord.from_path(IMG_PATH + 'cat1.jpg')

    img.rename('nyaa')
    assert img.attributes['name'] == 'nyaa' and file_exists('nyaa.jpg') == True

    img.rename('cat1')
    assert img.attributes['name'] == 'cat1' and file_exists('cat1.jpg') == True

  def test_find_many(self):
    self._reset_table()
    for f in fs.get_files(IMG_PATH):
      ImageRecord.from_path(f.path)
    names =  [r.attributes['name'] for r in ImageRecord.find_many(1, 3)]
    assert names == ['cat2', 'cat3', 'cat4']

  def test_delete_on_disk_option(self):
    func = lambda disk : ImageRecord.from_path(IMG_PATH+'temp.jpg').delete(disk)
    test = lambda : file_exists('temp.jpg')

    assert self._temp_img(func, test, False) == True
    assert self._temp_img(func, test, True) == False

  def test_from_path_unique_check_option(self):
    func = lambda unique : ImageRecord.from_path(IMG_PATH+'temp.jpg', unique)
    test = lambda : count_rows(self.img.conn, 'Image')

    rows = count_rows(self.img.conn, 'Image')

    assert self._temp_img(func, test, False) > rows

    rows = count_rows(self.img.conn, 'Image')
    assert self._temp_img(func, test, True) == rows

  def _reset_table(self):
    self.img.conn.execute("DROP TABLE Image")
    self.img.conn.execute("DROP TABLE ImageTag")
    self.img.conn.execute("DROP TABLE Tag")
    TestImageRecord.img = setup_record()

  def _temp_img(self, func, test, arg=None):
    if not file_exists('temp.jpg'):
      copyfile(IMG_PATH+'cat1.jpg', IMG_PATH+'temp.jpg')

    if arg is None:
      func()
    else:
      func(arg)
    result = test()

    if file_exists('temp.jpg'):
      os.remove(IMG_PATH+'temp.jpg')
    return result
