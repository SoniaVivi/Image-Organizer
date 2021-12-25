import cmd
from .image_controller import ImageController
from .database_controller import DatabaseController
from .tag_controller import TagController
import os

class CLI(cmd.Cmd):
  prompt = '(vivid) '
  controllers = {'db': None, 'img': None, 'tag': None}

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._set_controllers(test=True)

  def execute(self, sql, *args):
    return CLI.controllers['db'].execute(sql, *args)

  def _set_controllers(self, test=False):
    if not CLI.controllers['db']:
      CLI.controllers['db'] = DatabaseController(test=test)
      CLI.controllers['img'] = ImageController(db=CLI.controllers['db'])
      CLI.controllers['tag'] = TagController(db=CLI.controllers['db'])

if __name__ == '__main__':
  os.chdir(os.path.dirname(os.path.abspath(__file__)))
  CLI().cmdloop()
