from vivid import database_controller as dc
from vivid import image_controller as ic
from .helpers import IMG_PATH, THUMBNAIL_PATH, file_exists
from vivid import filesearch as fs
from pathlib import Path
import os
from shutil import copyfile

class TestImageController:

  db = dc.DatabaseController(True)
  img = ic.ImageController(db, True)

  def test_add_image(self):
    self._reset_table()
    self.img.add_image(f"{IMG_PATH}cat1.jpg")
    assert self.db.find_by('image', ('id', 1)) == {
                                                   'id': 1, 'name': 'cat1',
                                                   'path': IMG_PATH + 'cat1.jpg',
                                                   'hash': 'e3169ce9d046ad9c',
                                                   'image_type': 'jpg'
                                                  }
    results = self._thumbnails_helper([
                lambda : os.path.isdir(THUMBNAIL_PATH),
                lambda : file_exists('1.png', THUMBNAIL_PATH)
                ])
    assert results[0] == True
    assert results[1] == True

  def test_rename(self):
    self._reset_table()
    path = IMG_PATH + 'cat1.jpg'
    img = self.img.add_image(path)

    path = self.img.rename(path, 'nyaa')[1]
    assert self.db.find_by('Image', ('name', 'cat1')) or file_exists('cat1.jpg') == False
    assert self.db.find_by('Image', ('name', 'nyaa')) and file_exists('nyaa.jpg') == True

    path = self.img.rename(path, 'cat1')[1]
    assert self.db.find_by('Image', ('name', 'cat1')) and file_exists('cat1.jpg') == True
    assert self.db.find_by('Image', ('name', 'nyaa')) or file_exists('nyaa.jpg') == False

  def test_remove(self):
    self._reset_table()
    func = lambda disk : self.img.remove(IMG_PATH+'temp.jpg', disk)
    test = lambda : file_exists('temp.jpg')

    assert self._temp_img(func, test, True) == True
    assert self._temp_img(func, test, False) == False

  def test_add_image_unique_option(self):
    func = lambda uniq : self.img.add_image(IMG_PATH+'temp.jpg', unique=uniq)
    test = lambda : self.db.count('Image')

    rows = self.db.count('Image')

    assert self._temp_img(func, test, False) > rows

    rows = self.db.count('Image')
    assert self._temp_img(func, test, True) == rows

  def test_add_directory(self):
    self._reset_table()
    self.img.add_directory(IMG_PATH)
    assert self.db.count('Image') == 4

    self._reset_table()

    self.img.add_directory(IMG_PATH, False)
    assert self.db.count('Image') == 5
    records = [record['name'] for record in self.db.between('Image', 1, 5)]

    self._reset_table()

    assert records.sort() ==  ['cat2.jpg', 'cat3.jpg', 'cat4.jpg',
                               'cat1.jpg', 'cat.jpg'].sort()

  def test_existance_check(self):
    self._reset_table()
    self._temp_img(lambda *args: os.remove(f"{IMG_PATH}temp.jpg"),
                   lambda : self.img.existance_check())
    assert self.db.count('Image') == 0

    self._temp_img(lambda *args : 5,
                   lambda : self.img.existance_check())
    assert self.db.count('Image') == 1

  def _reset_table(self):
    self._remove_thumbnails()
    self.db.connection.execute("DROP TABLE Image")
    self.db.connection.execute("DROP TABLE ImageTag")
    self.db.connection.execute("DROP TABLE Tag")
    TestImageController.db.connection = self.db._setup_database(True)

  def _temp_img(self, func, test, arg=None, path=IMG_PATH):
    if not file_exists('temp.jpg'):
      copyfile(f"{path}cat1.jpg", f"{path}temp.jpg")
      self.img.add(f"{path}temp.jpg")

    try:
      func(arg)
      return test()
    except Exception as e:
      print(e)
    finally:
      if file_exists('temp.jpg'):
        os.remove(f"{path}temp.jpg")

  def _temp_folder(self, func, test, arg=None, path = f"{IMG_PATH}temp"):
    if not file_exists('temp'):
      Path(path).mkdir

    try:
      return self._temp_img(func, test, arg, path)
    except Exception as e:
      print(e)
    finally:
      if file_exists('temp'):
        os.rmdir(path)

  def _remove_thumbnails(self):
    if os.path.isdir(THUMBNAIL_PATH) == True:
      [os.remove(file.path) for file in fs.get_files(THUMBNAIL_PATH)]

  def _thumbnails_helper(self, tests):
    results = [test() for test in tests]
    self._remove_thumbnails()
    return results


