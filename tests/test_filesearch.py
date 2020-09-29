from .helpers import IMG_PATH
from vivid import filesearch

def test_get_files():
  assert [f.name for f in filesearch.get_files(IMG_PATH)] ==\
          ['cat.txt', 'cat2.jpg', 'cat.psd', 'notacat.txt', 'cat3.jpg',
           'cat4.jpg', 'cat1.jpg']

def test_get_directory_family():
  assert [f.name for f in filesearch.get_files(IMG_PATH, False)].sort() == (
          ['cat.txt', 'cat2.jpg', 'cat.psd', 'notacat.txt', 'cat3.jpg',
          'cat4.jpg', 'cat1.jpg', 'cat.jpg'].sort())
