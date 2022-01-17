# class Tag Controller

The TagController class is the only user that may directly modify the Tag and ImageTag table.

## Tagging images

### tag(image_id[int], tags[str]) # => None

---

Tags image with each tag name in tags. Creates the tag if it does not exist. Returns None.

```
>>> tag_con.tag(1, 'ocean tsunami blue')
>>> tag_con.all(1)
('ocean', 'tsunami', 'blue')
```

## Retrieving Tags

### all(value[str, int]) # => tuple

---

Value must be an image id or a tag name. If value is an int, returns all tags that the image id has. If value is a string, returns all records that has the tag.

```
>>> tag_con.all(1)
('ocean', 'tsunami', 'blue')
>>> tag_con.all('blue')
({'id': 1, 'name': 'beach', 'path': None, 'hash': None, 'image_type': None}, {'id': 2, 'name': 'sky', 'path': None, 'hash': None, 'image_type': None})
```

### find(tags[iterable]) # => tuple

---

Returns a tuple containing all images that has all the tags and none of the excluded tags. To exclude a tag put a '-' character in front of the tag name.

```
>>> tag_con.find(['ocean','blue'])
({'id': 1, 'name': 'beach', 'path': None, 'hash': None, 'image_type': None},)

>>> tag_con.find(['-ocean','blue'])
({'id': 2, 'name': 'sky', 'path': None, 'hash': None, 'image_type': None},)
```

## Removing tags

### remove(id[int], tag_name[str]) # => None

---

Removes tag from image. If tag has no entries after removal, deletes tag.

```
>>> tag_con.remove(1, 'ocean')
>>> tag_con.all(1)
('tsunami', 'blue')
```
