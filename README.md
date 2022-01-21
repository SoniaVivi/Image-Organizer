# Image Organizer

## Features

- Adding images in a top-level and/or nested directory

- Viewing properties of an image (name, location, hash, tags)

- Tagging Images

- Renaming images

- Finding the location of an image in a single double click

- Filtering images

- Blacklisting images and directories

## Testing

Tests can be ran using `pytest` in the root directory.

## User Guide

A user guide can be found in the top level directory of the repository named "user_guide.md" and is included in releases v1.5.0+.

## Documentation

Documentation can be found under the /docs directory in its respective module. Ex. `./vivid/docs` contains the documentation for `./vivid`.

Please note that documentation is still being written and may be partially incomplete or absent for various modules.

## User installation and updating

1. Download the latest release.

2. Unzip the attached file in your chosen directory.

3. Run vivid using `./vivid` in the newly extracted directory.

Follow the same steps when updating and choose to overwrite all files. All thumbnail and image data will be preserved

## Installing from source

1. Clone the repository

2. Create a virtual environment by running

   `python3 -m virtualenv [environment name]`

3. Activate the environment using
   `source [environment name]/bin/activate`

4. Install all dependencies using pip by running

   `python3 -m pip install -r ./requirements.txt`

### Known Issue

---

If .gif images appear as blank in the Sidebar preview and the terminal shows

`[ERROR ] [Image ] Error loading <[PATH TO IMAGE]>`

the problem lies with Kivy. To remedy this, edit line 91 of `[PATH TO VENV]/lib/python3.9/site-packages/kivy/core/image/img_pil.py`

From `img_ol.paste(img_tmp, (0, 0), img_tmp)` to `img_ol.paste(img_tmp, (0, 0))`

Why: Pillow throws a "Bad Transparency Mask" exception when the last argument is passed and Kivy then shows a blank image.

## Generating an executable

Follow the steps below "Installing from source" then run

`pyinstaller --paths . --onedir main.py`

Pyinstaller may not detect ./vivid.kv, ./fonts, the fleep package, and/or kivy_install. If this occurs copy and move the missing files/directories to ./dist/main.

## License

Vivid is released under the terms of the GPL-3.0-or-later license. Please refer to the LICENSE file.
