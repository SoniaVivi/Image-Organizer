Last Modified: 2.0-dev

# class Config

Config handles user settings and persistent runtime settings.

Current options:

- image_index
  - sort[str]. Default 'ASC'. Possible: 'DESC' or 'ASC'.
- image_controller
  - logging[str]. Default False. Possible: 'True' or 'False'.

## Setting

### set(section[str], attribute[str], value[str]) # => None

---

Sets section attribute to value.

## Reading

### read(section[str], attribute[str]) # => str

---

Returns section attribute value.

### section_attributes(section[str]) # => list

---

Parses through config and returns a list of strings containing the name of keys in section.

```
>>> Config().section_attributes('image_index_context_menu')
['image_tagging', 'image_renaming', 'image_removing', 'image_deleting', 'image_blacklisting', 'creator_updating', 'source_updating', 'folder_searching', 'hash_searching']
```

### section_items(section[str]) # => dict

---

Returns a dict containing the key name and value from section.

```
>>> Config().section_items('image_index_context_menu')
{'image_tagging': 'True', 'image_renaming': 'True', 'image_removing': 'True', 'image_deleting': 'False', 'image_blacklisting': 'False', 'creator_updating': 'True', 'source_updating': 'True', 'folder_searching': 'True', 'hash_searching': 'True'}
```

### exists(section[str], attribute[str]) # => bool

---

Returns true if attribute in section exists, else false.
