Last Modified: 1.5.0

# class Database Controller

The DatabaseController class is the sole handler of CRUD operations to the database. No other class may implement a method that modifies or reads from the database without utilizing DatabaseController.

## Usage Guidelines and Restrictions

Use execute() to execute sql operations not self.connection.

Only use execute() and sql_from_lists() in non-DatabaseController methods if the desired operation:

- Is significantly faster and/or more readable in sql.

- Cannot be implemented by included methods and has no general use.

DatabaseController may never be directly used by vivid_GUI except for the following operations:

- Retrieving images.

- Counting entries in a table.

- Getting the first or last record in the Image table.

- Listing Tags.

## Creating records

### create(table[str], attributes[dict]) # => int

---

Returns id of the newly created record.

```
>>> db = DatabaseController()

>>> db.create('Image', {'name': 'gurney_halleck',
                        'path': '/home/',
                        'hash': '1234ab',
                        'image_type': 'jpg'})
1
```

## Retrieving records

### find_by(table[str], attributes[dict, iterable], fetchall[bool]=False) # => dict, list, or None

---

If fetchall is False, returns first record matched or None if no records matched.

If fetchall is True, returns all records matched or an empty list.

Attributes can be a dict or an iterable containing an attribute pair.

```
>>> db.find_by('Image', {'id': 1, 'name': 'cat'})
{'id': 1, 'name': 'cat', 'path': '/home/user/Pictures/cat1.jpeg', 'hash': 'catcat4catcat', 'image_type': 'jpg'}

>>> db.find_by('Image', ('id', 2,))
{'id': 2, 'name': 'cat2', 'path': '/home/user/Pictures/cat0.png', 'hash': 'cat3catcat', 'image_type': 'png'}

>>> db.find_by('ImageTag', {'tag_id': 4}, True)
[{'id': 4, 'tag_id': 4, 'image_id': 70}, {'id': 5, 'tag_id': 4, 'image_id': 56}, {'id': 6, 'tag_id': 4, 'image_id': 68}]

```

### find_many(table[str], attributes[list]=[], \*\*kwargs) # => list

---

Returns a list of dicts containing matched record data or an empty list if no matches are found.

Keyword Arguments

- inclusive[bool] - Default True. When true, select records that match any of the criteria. When false, select records that match all criteria.

- exclude[list] - Default []. Do not select any records that match any of the criteria.

```
>>> db = DatabaseController()

>>> db.find_many('Tag', [{'id': 1}, {'id': 2}])
[{'id': 1, 'name': 'atreides'}, {'id': 2, 'name': 'harkonnen'}]

>>> db.find_many('Tag', exclude=[{'name': 'cat'}])
[{'id': 1, 'name': 'atreides'}, {'id': 2, 'name': 'harkonnen'}, {'id': 3, 'name': 'dog'}]
```

### between(table[str], start[int], stop[int]) # => list

---

Returns a list of dicts or an empty list.

```
>>> db.between('Image', 31, 45)
[{'id': 31, 'name': 'cat parade', 'path': '/home/user/Pictures/1234.png', 'hash': 'imagehash', 'image_type': 'png'}, ..., {'id': 45, 'name': 'cat birthday', 'path': '/home/user/Pictures/5678.png', 'hash': 'imagehash', 'image_type': 'jpg'}]
```

### search(table[str], attributes[dict]) # => list

---

Returns a list of dicts or an empty list.

```
>>> db.search('Tag', {'name': 'Ca'})
[{'id': 4, 'name': 'cat'}]

>>> db.search('Tag', {'name': 'Neo'})
[]
```

### get_first(table[str]) # => dict

---

Returns first record or an empty, nonexistent record with an id of 2 \*\* 63.

```
>>> db.get_first('ImageTag')
{'id': 1, 'tag_id': 1, 'image_id': 73}

db.get_first('ImageBlacklist')
{'id': 9223372036854775808, 'textable': None, 'textable_type': None}
```

### get_last(table[str]) # => dict

---

Returns last record or an empty, nonexistent record with an id of -1.

```
db.get_last('ImageTag')
{'id': 7, 'tag_id': 5, 'image_id': 67}

db.get_last('ImageBlacklist')
{'id': -1, 'textable': None, 'textable_type': None}
```

## Updating records

### update(table[string], id[int], new_values[iterable]) # => None

---

Updates a single record in the database. Returns None.

```
>>> db.get_last('Image')
{'id': 74, 'name': 'mislabeled image', 'path': '/home/user/Pictures/mislabeled image.jpeg', 'hash': 'shoggoth', 'image_type': 'jpg'}

>>> db.update('Image', 74, [('name', 'Charles Dexter Ward',), ('image_type', 'png',)])

>>> db.get_last('Image')
{'id': 74, 'name': 'Charles Dexter Ward', 'path': '/home/user/Pictures/mislabeled image.jpeg', 'hash': 'shoggoth', 'image_type': 'png'}
```

## Deleting records

### delete(table[str], attribute_pair[iterable]) # => None

---

Deletes all records matched. Returns None.

```
>>> db.count('Image')
5
>>> db.delete('Image', ['name', 'Yagami'])
>>> db.count('Image')
1
```

## Miscellaneous Methods

### get_columns(table[str]) # => list

---

Returns the columns in a table.

```
>>> db.get_columns('Image')
['id', 'name', 'path', 'hash', 'image_type']
```

### count(table[str]) # => int

---

Returns number of entries in a table.

```
>>> db.count('Image')
1
```

### exists(table[str], attribute[dict, iterable, None]=None) # => bool

---

If attribute is None, checks if table exists. Otherwise serves as a wrapper for find_by().

```
>>> db.exists('NonexistentTable')
False

>>> db.exists('Image', {'id': 5})
True
```

### unique(table[str], attribute[iterable]) # => bool

---

Returns true if attribute appears 0 or 1 times. Otherwise, false.

```
>>> db.unique('Tag', ('name', 'cat'))
True
```

### execute(sql_string[str], \*args) # => sqlite3.Cursor

---

Executes the sql string. In the future this method may be used to record changes in the database and allow for an 'undo-redo' feature.

```
>>> db.execute('SELECT * FROM ImageTag')
<sqlite3.Cursor object at 0x7fd55525bf10>
```

### sql_from_lists(names[list, str], values[iterable], joiner[str]) # => str

---

Returns an sql string. Typically used to match or ignore multiple attributes.

```
>>> db.sql_from_lists('T.id', [3,4,5,6], 'OR')
"T.id='3' OR T.id='4' OR T.id='5' OR T.id='6'"

>>> db.sql_from_lists(['id', 'name', 'id', 'name'], [3,'Cat',5,'Neko'], 'OR')
"id='3' OR name='Cat' OR id='5' OR name='Neko'"
```

### get_id(table[str], attributes[dict]) # => int or None

---

Returns id of the first matched record or None if not found.

```
>>> db.get_id('Image', {'name': 'Yog-Sothoth'})
5
```

### to_record(table[str], record_data[iterable]) # => dict

---

Returns a dict containing record data returned by an sql operation as values and table columns as keys.
