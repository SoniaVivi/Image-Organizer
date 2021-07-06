import sqlite3

class DatabaseController():
  def __init__(self, test=False, conn=None):
    if conn:
      self.connection = conn
    elif test:
      self.connection = self._setup_database(test)
    else:
      self.connection = sqlite3.connect('imagedb.db')
      self.image_table_exists()
  def create(self, table, attributes):
    sql = '''INSERT INTO %s(%s)
             VALUES (%s)''' % (table, ','.join(attributes.keys()),
                              ('?,' * len(attributes.keys()))[0:-1])
    try:
      cur = self.connection.execute(sql, tuple(attributes.values()))
      self.connection.commit()
      return self.connection.execute('SELECT max(id) FROM %s' % (table,)).fetchone()[0]
    except Exception as e:
      print(e)

  def update(self, table, id, new_values):
    for attribute in new_values:
      self.connection.execute('''UPDATE %s SET %s = ? WHERE id = ?''' %
                       (table, attribute[0]), (attribute[1], str(id),))

    self.connection.commit()

  def delete(self, table, attribute_pair):
    self.connection.execute('''DELETE FROM %s WHERE %s=?''' %
                                                    (table, attribute_pair[0]),
                                                    (attribute_pair[1],))
    self.connection.commit()

  def find_by(self, table, attribute_pair):
    sql = '''SELECT * FROM %s WHERE %s = ?''' % (table, attribute_pair[0],)
    record = self.connection.execute(sql, (attribute_pair[1],)).fetchone()
    if record:
      return dict(zip(self.get_columns(table), record))

  def find_many(self, table, start, stop):
    total = self.count(table)
    return [self.find_by(table, ['id', n])
              for n in range(start, stop+1) if n <= total]

  def search(self, table, column, query):
    sql = "SELECT id FROM %s WHERE %s LIKE '%s'" % \
            (table, column, f"%{query}%",)
    results = self.connection.execute(sql).fetchall()
    return [self.find_by('Image', ('id', result[0])) for result in results]

  def next_id(self, table, value):
    sql = '''SELECT id FROM %s WHERE id > %s'''
    return self.connection.execute(sql % (table, value,)).fetchone()[0]

  def get_columns(self, table):
    cols = self.connection.execute('''PRAGMA table_info(%s)''' % (table,))
    cols = cols.fetchall()
    return None if len(cols) == 0 else [row[1] for row in cols]

  def count(self, table):
    return self.connection.execute('''SELECT count(*) FROM %s''' % table).fetchone()[0]

  def exists(self, table, attribute=None):
    if not attribute:
      result = self.connection.execute('''SELECT name
                                          FROM sqlite_master
                                          WHERE type='table'
                                          AND name='%s' ''' % (table,)).fetchone()
      return True if result != None else False
    return True if self.find_by(table, attribute) else False

  def unique(self, table, attribute):
    sql = "SELECT id FROM {} WHERE {}=?".format(table, attribute[0])
    result = self.connection.execute(sql, (attribute[1],)).fetchall()
    return True if len(result) <= 1 else False

  def image_table_exists(self):
    exists = self.connection.execute('''SELECT count(name)
                                        FROM sqlite_master
                                        WHERE type='table'
                                        AND name='Image' ''').fetchone()[0]
    if exists == 0:
      print('Setting up database')
      self._setup_database(False)
      print('Database setup complete')

  def _setup_database(self, test):
    conn = sqlite3.connect('imagedb.db') if not test else sqlite3.connect(':memory:')
    conn.execute('''CREATE TABLE Image (id integer primary key, name text,
                          path text, hash text, image_type text)''')
    conn.execute('''CREATE TABLE Tag (id integer primary key, name text)''')
    conn.execute('''CREATE TABLE ImageTag (id integer primary key,
                          tag_id integer, image_id int)''')
    conn.commit()
    return conn if test == True else None
