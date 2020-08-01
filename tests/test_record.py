from vivid import record as vivid
from .helpers import table_exists, count_rows
import sqlite3

def test_setup():
  conn = vivid.setup_database(True)
  assert table_exists(conn, 'Image') == True
  assert table_exists(conn, 'Tag') == True
  assert table_exists(conn, 'ImageTag') == True

class TestRecord:

  conn = vivid.setup_database(True)

  def test_create(self):
    vivid.Record.conn = self.conn
    records = [
              [{'name': 'f', 'path': 'f'}, 'Image'],
              [{'name': 'f', 'path': 'f', 'hash': 'f', 'extension': 'f'}, 'Image'],
              [{'name': 'f'}, 'Tag'], [{'ffff': 'f'}, 'Tag']
              ]
    records = [vivid.Record(record[1], record[0]) for record in records]
    [record.create() for record in records ]

    assert count_rows(self.conn, 'Image') == 2
    assert count_rows(self.conn, 'Tag') == 1

  def test_columns(self):
    assert vivid.Record.get_columns('Dog') == None
    assert vivid.Record.get_columns('Image') ==\
                                   ['id', 'name', 'path', 'hash', 'extension']
  def test_find_many(self):
    records = vivid.Record.find_many(1, 2, 'Image')
    assert len(records) == 2
    assert [record.attributes for record in records] ==\
          [{'id': 1, 'name': 'f', 'path': 'f', 'hash': None, 'extension': None},
           {'id': 2, 'name': 'f', 'path': 'f', 'hash': 'f', 'extension': 'f'}]

  def test_save(self):
    def save_records():
      record_info = ['Tag', 10]
      for record in self._create_records(*record_info):
        record.save()

    rows = count_rows(self.conn, 'Tag')
    save_records()

    assert rows < count_rows(self.conn, 'Tag')
    record = vivid.Record.find_by(['id', count_rows(self.conn, 'tag')], 'Tag')

    record.attributes['name'] = 'meow'
    record.save()

    record = vivid.Record.find_by(['id', record.attributes['id']], 'Tag')
    assert record.attributes['name'] == 'meow'
    assert vivid.Record.find_by(['id', 3], 'Tag').attributes['id'] != 'meow'

  def _create_records(self, table, count):
    return [vivid.Record(table, {'name': str(n)}) for n in range(0, count)]
