from configparser import ConfigParser
from os.path import isfile

class Config():
  DEFAULTS = (('image_index', {'sort': 'ASC'},),)

  def __init__(self, path='./config'):
    if not isfile(path):
      with open(path, 'a+'): pass
    self.path = path
    self._setup()

  def set(self, section, attribute, value):
    parser = ConfigParser()
    parser.read(self.path)
    parser[section][attribute] = value
    with open(self.path, 'w') as configfile:
      parser.write(configfile)

  def read(self, section, attribute):
    parser = ConfigParser()
    parser.read(self.path)
    return parser[section][attribute]

  def _setup(self):
    parser = ConfigParser()
    parser.read(self.path)
    for section_data in self.DEFAULTS:
      if section_data[0] not in parser:
        parser[section_data[0]] = section_data[1]
      for attribute_name, value in section_data[1].items():
        if attribute_name not in parser[section_data[0]]:
          parser[section_data[0]][attribute_name] = value
    with open(self.path, 'w') as configfile:
      parser.write(configfile)
