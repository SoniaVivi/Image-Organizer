Last Modified: 2.0-dev

# class Image Controller

The ImageController is the sole handler of creating, updating, and deleting images. It is also the only class that may directly utilize the Blacklist class. No other class may implement or be used to implement a method for modifying image record data without utilizing ImageController.

## Adding Images

### add(path[str], \*\*kwargs) # => self

---

Serves as a wrapper for add_image() and add_directory(). Please refer to their respective documentation for details.

### add_image(path[str], \*\*kwargs) # => self

---

Adds image to the database. Path must be an absolute path.

Keyword Arguments:

- blacklist_check - Default True. When true, checks if the path or hash is blacklisted.

- unique - Default False. When true, only adds image if the hash is unique.

- scramble_name - Default False. When true, saves a random string as the image name instead of the image file name. Overrides the hash_as_name argument.

- hash_as_name - Default False. When true, saves the image hash as the image name.

```
>>> img_con.add_image('/home/usr/Pictures/pupper.png')
<vivid.image_controller.ImageController object at 0x7fc666534f70>
>>> db.get_first('Image')
{'id': 1, 'name': 'pupper', 'path': '/home/usr/Pictures/pupper.png', 'hash': '1a2b3c4d5e', 'image_type': 'png'}
```

### add_directory(path[str], toplevel_only[bool]=False, \*\*kwargs) # => self

---

Adds all images in directory to the database. Path must be an absolute path.

When toplevel_only is False, adds images in subdirectories.

Keyword Arguments: Please refer to add_image() for details.

```
>>> db.count('Image')
1
>>> img_con.add_directory('/home/usr/Pictures/')
<vivid.image_controller.ImageController object at 0x7fc666534f70>
>>> db.count('Image')
343
```

## Retrieving Thumbnails

### get_thumbnail(image_id[int]) => str

---

Returns path of the thumnail.

```
>>> img_con.get_thumbnail(1)
'./thumbnails/1.png'
```

## Updating Images

### rename(path[str], new_name[str], on_disk[bool]=True) # => tuple

---

Returns image path.

When on_disk is:

- True, renames image in database and on disk.

- Otherwise, renames image only in database.

### recreate_thumbnails() # => None

---

Overwrites and recreates all thumbnails present in the Image table.

```
img_con.recreate_thumbnails()
```

### update_metadata(img_ids[list, int], metadata[dict]) # => None

---

Updates values in specified images.

Use only if no method directly corresponds to the respective attribute.

## Deleting Images

### remove(path[str], \*\*kwargs) # => self

---

Removes image and thumbnail from the database. Returns self.

Keyword Arguments:

- blacklist - Default False.
  Options:
  - 'hash' - Blacklists image hash
  - 'path' - Blacklists image path.
  - 'all' - Blacklists both.
- db_only - Default True. When false, deletes images from disk.

```
>>> db.count('Image')
1
>>> img_con.remove('/home/usr/Pictures/pupper.png')
<vivid.image_controller.ImageController object at 0x7fc666534f70>
>>> db.count('Image')
0
```

## existence_check() # => None

---

Removes all images in database that does not exist.

## Blacklisting

### textable and textable_type

---

textable refers to a string that is one of the following:

- An absolute path to an image

- An absolute path to a directory

- Hash

Valid textable_types are 'path', 'directory', and 'hash', respectively.

### blacklist_image(textable[str], textable_type[str]) # => self

---

Blacklists an image. Textable must be an absolute path or an image hash. Textable type must correctly correspond to textable. Returns self.

```
>>> db.count('ImageBlacklist')
0
>>> img_con.blacklist_image('/home/usr/Pictures/doggo.png', 'path')
<vivid.image_controller.ImageController object at 0x7f9790faef70>
>>> db.get_first('ImageBlacklist')
{'id': 1, 'textable': '/home/usr/Pictures/doggo.png', 'textable_type': 'path'}
```

### blacklist_directory(path[str]) # => self

---

Blacklists a directory. Path must be an absolute path. Returns self.

```
>>> db.count('ImageBlacklist')
1
>>> img_con.blacklist_directory('/home/usr/Pictures/birds/')
<vivid.image_controller.ImageController object at 0x7f9790faef70>
>>> db.get_last('ImageBlacklist')
{'id': 1, 'textable': '/home/usr/Pictures/birds/', 'textable_type': 'directory'}
```

### is_blacklisted(data[iterable]) # => bool

---

Checks if path, directory, or hash is blacklisted.

Data must be in the following format: [textable, textable_type]

## Plugins and Middleware

### Structure

---

Plugins must contain the following:

- A string named "title"

- A string named "description"

They may contain functions named the following:

- before

- after

add_image before and after functions are passed 2 args in the following order:

- Data from the image to be added

- The ImageController instance that is adding the image

Currently only plugins for #add_image are supported.

### add_middleware(key[str], \*\*kwargs) # => None

---

Adds

- A function

or

- A group of functions from a file

to ImageController.middleware

Keyword Arguments:

- path - Default None. Must be a string containing a path if passed.

- middleware - Default {}. Must be a dict containing "before" or "after" keys and respective functions if passed.

```
>>> ImageController.add_middleware("add_image", path="./vivid_GUI/plugins/add_image/")
```
