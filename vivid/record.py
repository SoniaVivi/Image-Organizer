from PIL import Image
import os
import imagehash
import fleep
import sqlite3

class Record:

  conn = sqlite3.connect('imagedb.db')
  table = (None,)

  def __init__(self, table, attributes={}):
    self.table = table
    self.attributes = attributes if type(attributes) is dict else {}

  def create(self):
    details = self.attributes
    sql = '''INSERT INTO %s(%s)
             VALUES (%s)''' % (self.table, ','.join(list(details.keys())),
                              ('?,' * len(details))[0:-1])
    try:
      cur = self.conn.execute(sql, tuple(details.values()))
      self.conn.commit()
      return self.find_by(['id', cur.lastrowid], self.table)
    except Exception as e:
      print(e)

  def save(self):
    if 'id' not in self.attributes:
      return self.create()
    for key in self.attributes.keys():
      if key == 'id':
        continue
      self.conn.execute('''UPDATE %s SET %s=? WHERE id = ?''' %\
                       (self.table, key,),
                       (self.attributes[key], self.attributes['id'],))
    self.conn.commit()

  def delete(self):
    if 'id' in self.attributes:
      self.conn.execute('''DELETE FROM %s WHERE id=?''' % (self.table,),
                                                    (self.attributes['id'],))
      self.conn.commit()

  def columns(self):
    return self.get_columns(self.table)

  @staticmethod
  def get_columns(table):
    cols = Record.conn.execute('''PRAGMA table_info(%s)''' % (table,))
    cols = cols.fetchall()
    return None if len(cols) == 0 else [row[1] for row in cols]

  @classmethod
  def set_connection(cls, conn):
    if type(conn) is str:
      Record.conn = sqlite3.connect(conn)
    elif type(conn) is sqlite3.Connection:
      Record.conn = conn
    else:
      return False
    return True

  @classmethod
  def find_by(cls, attribute, table=None):
    if not table:
      table = cls.table[0]
    sql = '''SELECT * FROM %s WHERE %s = ?''' % (table, attribute[0],)
    record = Record.conn.execute(sql, (attribute[1],)).fetchone()
    if record:
      return cls(table=table, attributes=dict(zip(Record.get_columns(table), record)))

  @classmethod
  def find_many(cls, start, stop, table=None):
    if not table:
      table = cls.table[0]
    records = []
    for n in range(start, stop+1):
      records.append(Record.find_by(['id', n], table))
    return records

def setup_database(test=False):
  conn = sqlite3.connect('imagedb.db') if not test else sqlite3.connect(':memory:')
  conn.execute('''CREATE TABLE Image (id integer primary key, name text,
                        path text, hash text, extension text)''')
  conn.execute('''CREATE TABLE Tag (id integer primary key, name text)''')
  conn.execute('''CREATE TABLE ImageTag (id integer primary key,
                        tag_id integer, image_id int)''')
  conn.commit()
  return conn if test == True else None
