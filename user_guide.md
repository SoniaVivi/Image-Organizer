# User Guide

## Terminology:

- Sidebar - Left side container where image previews and associated image data is shown.

- Thumbnails - Small, rectangular previews of images generated when adding images.

- Image Index - The initial page shown on startup where image thumbnails are displayed.

- Toolbar - Top row containing buttons to switch pages, open modals, search images, and more.

- Tag List - Can be displayed and exited by clicking on the toolbar button labeled "Tag List".

- Statistics Page - Displays database statistics and has a button to verify that images present in the database exist on the disk. Can be opened by clicking on the toolbar button labeled "Stats".

- Preferences - User preferences to modify the GUI behavior. Can be opened by clicking on the toolbar button labeled "Preferences".

- Search bar - White, rectangular element in the far right side of the toolbar.

## Adding Image options

There are options to modify how images are saved in the top of the add image modal. **None of these options makes any changes to the image file itself.**

## ImageIndex Keybindings

- Page-down - Show X new images and scroll to the last image if the active widget is Workspace.

- Home - Scroll to the top image if the active widget is Workspace.

- End - Scroll to the last image without showing new images if the active widget is Workspace.

## Making Selections

Images can be selected by left clicking on image thumbnails.

Keybindings:

- Ctrl + Click (on a non-selected image) - Selects another image while retaining the current selection.

- Ctrl + Click (on a selected image) - Removes the image from the current selection.

- Shift + Click - Selects all images from the last selected image to the newly clicked image while retaining the current selection.

## Context Menu

The Context menu can be opened by right clicking in the workspace. Menu actions affects all selections.

### Image Index

---

Any number of item selections:

- Tagging opeartions.

- Removing and deleting.

- Blacklisting

Only single item selections:

- Renaming images

### Tag list

---

Any number of item selections:

- Searching by selected tags

## Sidebar

The Sidebar shows the last selected image and its associated data.

Sidebar image preview operations:

- Click - Open a large preview.

- Double click - Open in nautilus (linux) or opens file (windows).

## Searching

### Tags

---

Tags can be searched by using the Searchbar or Tag List. Images are only presented if they have all of the searched tags and no excluded tag. To exclude a tag put a "-" in front of the tag name when using the Searchbar.

### Folders and names

---

The Searchbar also supports searching by image name and folder.

## Miscellaneous

One can alter the order in which images are displayed by clicking the Preferences button and selecting a Sort Option.

To verify that all images exist on disk click on the Stats button, then on the button labeled "Recheck Images". Any image that is not found on the disk is removed from the database and its thumbnail deleted.
