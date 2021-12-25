from tests.helpers import IMG_PATH
from vivid.cli import CLI
from vivid.database_controller import DatabaseController as dc
from vivid.image_controller import ImageController as ic
from vivid.tag_controller import TagController as tc

class TestCLI():
  cli = CLI()
  db = dc(test=True)
  img = ic(db=db)
  tag = tc(db=db)

  def test_execute(self):
    columns = [col[1] for col in self.cli.execute(f"PRAGMA table_info(Image)")]
    assert columns == self.db.get_columns('Image')

  def test_run(self):
    assert self.cli.run('db.create("Image", {"name": "f"}') ==\
           self.db.create("Image", {"name": "f"})
    assert self.cli.run(f"img.add('Image', {IMG_PATH}cat1.jpg)") ==\
           self.img.add("Image", IMG_PATH+'cat1.jpg')
    assert self.cli.run(f"tag.tag(1, 'cat')") == self.tag.tag(1, 'cat')
