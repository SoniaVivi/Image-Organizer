import sqlite3
from vivid.filesearch import get_files

IMG_PATH = 'tests/test_images/'

def table_exists(conn, table_name):
  conn = conn.execute('''SELECT name
                  FROM sqlite_master
                  WHERE type='table'
                  AND name='%s' ''' % (table_name,)).fetchone()
  return True if conn != None else False

def count_rows(conn, table):
    return conn.execute('''SELECT count(*) FROM %s''' % table).fetchone()[0]

def file_exists(name, path=IMG_PATH):
  for f in get_files(path):
    if name == f.name:
      return True
  return False

