from vivid import database_controller as vivid
import sqlite3

class TestDatabaseController:
  db = vivid.DatabaseController(test=True)

  def test_setup(self):
    assert self.db.exists('Image') == True
    assert self.db.exists('Tag') == True
    assert self.db.exists('ImageTag') == True
    assert self.db.exists('ImageBlacklist') == True

  def test_create(self):
    records = [
                ['Image', {'name': 'f', 'path': 'f'}],
                ['Image', {'name': 'f', 'path': 'f', 'hash': 'f', 'image_type': 'f'}],
                ['Tag', {'name': 'f'}, 'Tag']
              ]

    [self.db.create(record[0], record[1]) for record in records]
    assert self.db.count('Image') == 2
    assert self.db.count('Tag') == 1

  def test_columns(self):
    assert self.db.get_columns('Dog') == None
    assert self.db.get_columns('Image') ==\
                                   ['id', 'name', 'path', 'hash', 'image_type']

  def test_between(self):
    records = self.db.between('Image', 1, 2)
    assert len(records) == 2
    assert records ==\
          [{'id': 1, 'name': 'f', 'path': 'f', 'hash': None, 'image_type': None},
           {'id': 2, 'name': 'f', 'path': 'f', 'hash': 'f', 'image_type': 'f'}]

  def test_find_many(self):
    self.db.create('Image', {'name': 'f'})
    assert len(self.db.find_many('Image', [{'name': 'f'}])) == 3
    assert len(self.db.find_many('Image', [{'image_type': 'f'}, {'path': 'f'}]))\
            == 2
    assert len(self.db.find_many('Image',
                                 [{'name': 'f'}, {'hash': 'f'}],
                                  inclusive=False)) == 1
    assert len(self.db.find_many('Image',
                                 [{'name': 'f'}], exclude=[{'hash': 'f'}])) == 2
    assert len(self.db.find_many('Image', exclude=[{'hash': 'f'}])) == 2

  def test_delete(self):
    row_count = self.db.count('Image')
    self.db.delete('Image', ('id', 1))
    assert row_count > self.db.count('Image')

  def test_unique(self):
    record = ['Image',
              {'name': 'g', 'path': 'f', 'hash': 'f', 'image_type': 'f'}]

    self.db.create(record[0], record[1])
    assert self.db.unique('Image', ('name', 'g')) == True

    self.db.create(record[0], record[1])
    assert self.db.unique('Image', ('name', 'g')) == False

