# Image Organizer

**Features**

- Adding images in a top-level and/or nested directory

- Viewing properties of an image (name, location, hash, tags)

- Tagging Images

- Renaming images

- Finding the location of an image in a single double click

- Filtering images

- Blacklisting images and directories

**Testing**

Tests can be ran using `pytest` in the root directory.

**User installation and updating**

1. Download the latest release.

2. Unzip the attached file in your chosen directory.

3. Run vivid using `./vivid` in the newly extracted directory.

Follow the same steps when updating and overwrite all files. All thumbnail and image data will be preserved

**Installing from source**

1. Clone the repository

2. Create a virtual environment by running

   `python3 -m virtualenv [environment name]`

3. Activate the environment using
   `source [environment name]/bin/activate`

4. Install all dependencies using pip by running

   `python3 -m pip install -r ./requirements.txt`

**Generating an executable**

Follow the steps below "Installing from source" then run

`pyinstaller --paths . --onedir main.py`

Pyinstaller may not detect ./vivid.kv, ./fonts, the fleep package, and/or kivy_install. If this occurs copy and move the missing files/directories to ./dist/main.

**License**

Vivid is released under the terms of the GPL-3.0-or-later license. Please refer to the LICENSE file.
