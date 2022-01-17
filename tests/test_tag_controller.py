from vivid import database_controller as dc
from vivid import image_controller as ic
from vivid import tag_controller as tc
from .helpers import CURRENT_PATH, IMG_PATH

class TestTagController:
  db = dc.DatabaseController(True)
  img = ic.ImageController(db, True, use_blacklist=False)
  tag = tc.TagController(db)

  def test_create(self):
    self.img.add_image(f"{IMG_PATH}cat1.jpg")
    self.img.add_image(f"{IMG_PATH}cat2.jpg")
    self.tag._create('Cat')
    self.tag._create('♡Meow♡')

    assert self.db.count('Tag') == 2

    self.tag._create('Cat')

    assert self.db.count('Tag') == 2

  def test_tag_image(self):
    self.tag.tag(1, 'Cat')
    assert self.db.find_by('ImageTag', ('image_id', 1)) == {'id': 1, 'image_id': 1, 'tag_id': 1}
    assert self.db.find_by('Tag', ('name', 'cat')) == {'id': 1, 'name': 'cat'}

    self.tag.tag(1, 'Cat')

    assert self.db.count('ImageTag') == 1

    self.tag.tag(1, '♡Meow♡')

    assert self.db.count('Tag') == 2
    assert self.db.count('ImageTag') == 2

  def test_all(self):
    self.tag.tag(1, 'Nyaa')
    assert self.tag.all(1) == ('cat', '♡meow♡', 'nyaa')

    assert self.tag.all('♡meow♡') == (self.db.find_by('Image', {'id': 1}),)

  def test_remove(self):
    self.tag.remove(1, 'cat')

    assert self.db.count('ImageTag') == 2
    assert self.db.count('Tag') == 2
    assert self.tag.all(1) == ('♡meow♡', 'nyaa')

  def test_find(self):
    self.img.add_image(f"{IMG_PATH}cat2.jpg")
    self.tag.tag(2, 'Nyaa')

    assert self.tag.find(('♡meow♡', 'nyaa')) ==\
                                          (self.db.find_by('Image', {'id': 1}),)
    self.tag.tag(2, '♡Meow♡')
    self.tag.tag(2, 'Kitty')

    assert self.tag.find(('♡meow♡', 'nyaa', 'kitty')) ==\
                                          (self.db.find_by('Image', {'id': 2}),)
    self.tag.tag(3, "meowb")
    self.tag.tag(3, "nyaa")
    self.tag.tag(3, "kitty")

    assert self.tag.find(('nyaa', 'kitty', '-meowb')) == (self.db.find_by('Image', {'id': 2}),)

