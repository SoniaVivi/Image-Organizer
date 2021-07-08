from kivy.uix.boxlayout import BoxLayout
from vivid.database_controller import DatabaseController
from vivid.image_controller import ImageController
from .image_index_container import ImageIndexContainer
from vivid.tag_controller import TagController
from .sidebar import Sidebar
from datetime import datetime, timedelta

class IndexWrapper(BoxLayout):
  img_controller = ImageController()
  db_controller = DatabaseController()
  tag_controller = TagController()

  def __init__(self, **kwargs):
    super(IndexWrapper, self).__init__(**kwargs)
    self.orientation = 'horizontal'
    self.sidebar = Sidebar()
    self.index = ImageIndexContainer(set_preview=self.set_preview,
                                     rename_image=self.rename_image)
    self.add_widget(self.sidebar)
    self.add_widget(self.index)
    self.last_update = datetime.now()

  def set_preview(self, data=None):
    self.sidebar.img_data = data if data else self.sidebar.empty_data()
    self.sidebar.update_children()

  def rename_image(self, thumbnail, in_database, on_disk):
    self.rename_properties = {'in_database': in_database, 'on_disk': on_disk}
    self.thumbnail = thumbnail
    self.sidebar.rename()

  def update_thumbnail(self, data):
    time = datetime.now()
    if time - self.last_update < timedelta(seconds=1):
      return

    self.last_update = time
    new_path = ('path', self.thumbnail().data['path'],)

    if 'name' in data:
      new_path = self.img_controller.rename(
                                          new_path[1],
                                          data['name'],
                                          self.rename_properties['on_disk'],
                                          self.rename_properties['in_database']
                                          )
    updated_data = self.db_controller.find_by('Image', new_path)
    updated_data['tags'] = self.tag_controller.all(updated_data['id'])
    self.thumbnail().update(updated_data)
    self.set_preview(updated_data)
