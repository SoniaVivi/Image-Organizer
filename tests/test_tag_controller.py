from vivid import database_controller as dc
from vivid import image_controller as ic
from vivid import tag_controller as tc
from .helpers import CURRENT_PATH, IMG_PATH

class TestTagController:
  db = dc.DatabaseController(True)
  img = ic.ImageController(db, True)
  tag = tc.TagController(db)

  def test_create(self):
    self.img.add_image(f"{IMG_PATH}cat1.jpg")
    self.tag._create('Cat')
    self.tag._create('♡Meow♡')

    assert self.db.count('Tag') == 2

    self.tag._create('Cat')

    assert self.db.count('Tag') == 2

  def test_tag_image(self):
    self.tag.tag(1, 'Cat')

    assert self.db.find_by('ImageTag', ('image_id', 1)) == {'id': 1, 'image_id': 1, 'tag_id': 1}
    assert self.db.find_by('Tag', ('name', 'Cat')) == {'id': 1, 'name': 'Cat'}

    self.tag.tag(1, 'Cat')

    assert self.db.count('ImageTag') == 1

    self.tag.tag(1, '♡Meow♡')

    assert self.db.count('Tag') == 2
    assert self.db.count('ImageTag') == 2

  def test_all(self):
    self.tag.tag(1, 'Nyaa')
    assert self.tag.all(1) == ('Cat', '♡Meow♡', 'Nyaa')

    assert self.tag.all('♡Meow♡') == (self.db.find_by('Image', {'id': 1}),)

  def test_remove(self):
    self.tag.remove(1, 'Cat')

    assert self.db.count('ImageTag') == 2
    assert self.db.count('Tag') == 2
    assert self.tag.all(1) == ('♡Meow♡', 'Nyaa')

  def test_find(self):
    self.img.add_image(f"{IMG_PATH}cat2.jpg")
    self.tag.tag(2, 'Nyaa')

    assert self.tag.find(('♡Meow♡', 'Nyaa')) ==\
                                          (self.db.find_by('Image', {'id': 1}),)
    self.tag.tag(2, '♡Meow♡')
    self.tag.tag(1, 'Kitty')

    assert self.tag.find(('♡Meow♡', 'Nyaa', '-Kitty')) ==\
                                          (self.db.find_by('Image', {'id': 2}),)
