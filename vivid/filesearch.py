import os

def get_directory_family(path):
  stack = []
  stack.append(get_files(path))
  for elt in stack:
    for entry in elt:
      if os.path.isdir(entry.path):
        stack.append(get_files(entry.path))
      else:
        yield entry

def get_files(path):
  with os.scandir(path) as dirs:
    for entry in dirs:
      yield entry
