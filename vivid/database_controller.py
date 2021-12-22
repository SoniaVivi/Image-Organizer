import sqlite3

class DatabaseController():
  def __init__(self, test=False, conn=None):
    if conn:
      self.connection = conn
    elif test:
      self.connection = self._setup_database(test)
    else:
      self.connection = sqlite3.connect('imagedb.db')
      for table in ['Image', 'Tag', 'ImageTag']:
        self._table_exists(table)

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

  def find_by(self, table, attributes, fetchall=False):
    sql = ''
    if type(attributes) != dict:
      sql = f"SELECT * FROM {table} WHERE {attributes[0]} = \"{attributes[1]}\""
    else:
      sql = f"SELECT * FROM {table} WHERE "
      for (key, value) in attributes.items():
        sql += f"{key} = '{value}' AND "
      sql = sql[0:-5]

    records = None

    if fetchall:
      records = self.connection.execute(sql).fetchall()
    else:
      records = self.connection.execute(sql).fetchone()

    if records:
      if not fetchall:
        return self._to_record(table, records)
      else:
        return [self._to_record(table, record) for record in records]
    return records

  def find_many(self, table, start, stop, asc=True):
    sql = f"SELECT * FROM {table} WHERE id BETWEEN {start} AND {stop}"
    results = self.connection.execute(sql).fetchall()
    return [self._to_record(table, result) for result in results if result]

  def search(self, table, attributes):
    sql = f"SELECT id FROM {table} WHERE "
    for (column, value) in attributes.items():
      sql += f"{column} LIKE '%{value}%' AND "

    sql = sql[0:-5]
    results = self.connection.execute(sql).fetchall()
    return [self.find_by('Image', ('id', result[0])) for result in results]

  def next_id(self, table, value, asc=True):
    operator = '>' if asc else '<'
    order_by = 'ASC' if asc else 'DESC'
    sql = '''SELECT id FROM %s WHERE id %s %s ORDER BY id %s'''
    return self.connection.execute(sql %
                              (table, operator, value, order_by,)).fetchone()[0]

  def get_first(self, table):
    return self._get_limit(table, False)

  def get_last(self, table):
    return self._get_limit(table)

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

  def _table_exists(self, table_name):
    exists = self.connection.execute(f"SELECT count(name)\
                                        FROM sqlite_master\
                                        WHERE type='table'\
                                        AND name='{table_name}' ").fetchone()[0]
    if exists == 0:
      print(f"Creating table {table_name}")
      self._setup_database(False, [table_name])

  def _to_record(self, table, record_data):
    return dict(zip(self.get_columns(table), record_data))

  def _get_limit(self, table, asc=True):
    order_by = 'DESC' if asc else 'ASC'
    placholder_id = -1 if asc else 2 ** 63

    columns = self.get_columns(table)
    record_data = self.connection.execute(
                                  "SELECT * FROM %s ORDER BY id %s LIMIT 1" %
                                                  (table, order_by)).fetchone()
    if not record_data:
      record_data = [None for _ in range(0, len(columns))]
      record_data[0] = placholder_id
    return dict(zip(columns, record_data))

  def _setup_database(self, test, tables=['Image', 'Tag', 'ImageTag']):
    conn = sqlite3.connect('imagedb.db') if not test else sqlite3.connect(':memory:')
    table_sql = {
                  'Image':'''CREATE TABLE Image
                    (id integer primary key,
                     name text, path text,
                     hash text,
                     image_type text)''',
                  'Tag':'''CREATE TABLE Tag
                    (id integer primary key, name text)''',
                  'ImageTag':'''CREATE TABLE ImageTag
                    (id integer primary key, tag_id integer, image_id int)'''
                }
    for table in tables:
      conn.execute(table_sql[table])
    conn.commit()
    return conn if test == True else None
