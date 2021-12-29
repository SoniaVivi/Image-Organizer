from kivy.core.window import Window
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput
from kivy.app import App
from kivy.clock import Clock
from datetime import datetime, timedelta
from platform import system
import os
from vivid.database_controller import DatabaseController
from vivid.image_controller import ImageController
from vivid.tag_controller import TagController
from .store import Store

class Sidebar(BoxLayout):
  img_controller = ImageController()
  db_controller = DatabaseController()
  tag_controller = TagController()

  def __init__(self, **kwargs):
    super(Sidebar, self).__init__(**kwargs)
    self.img_data = self.empty_data()
    self.id = 'sidebar'
    self.update_children()
    self.last_update = datetime.now()
    Store.dispatch('set_preview_image', self.set_preview)
    Store.dispatch('rename_image', self.rename_image)
    Store.dispatch('update_thumbnail', self.update_thumbnail)

  def empty_data(self):
    return {'name': '', 'path': '', 'hash': '', 'image_type': '', 'tags': ''}

  def update_children(self):
    self.clear_widgets()
    if not 'tags' in self.img_data:
      self.img_data['tags'] = ('')

    field_data = [
                  ("Name", self.img_data['name']),
                  ("Path", self.img_data['path']),
                  ("Hash", self.img_data['hash']),
                  ("Format", self.img_data['image_type']),
                  ("Tags", ", ".join(self.img_data['tags']))
                 ]
    self.add_widget(SidebarPreview(source=self.img_data['path']))
    for data in field_data:
      self.add_widget(SidebarField(data[0], data[1]))

  def rename(self):
    self.children[4].editable_field(self.img_data['name'])

  def set_preview(self, data=None):
    self.img_data = data if data else self.empty_data()
    self.update_children()

  def rename_image(self, thumbnail, in_database, on_disk):
    self.rename_properties = {'in_database': in_database, 'on_disk': on_disk}
    self.thumbnail = thumbnail
    self.rename()

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

class SidebarField(BoxLayout):
  def __init__(self, field_name, field_value, **kwargs):
    super(SidebarField, self).__init__(**kwargs)
    self.name_field = SidebarText(text=self.format_text(field_name),
                                  size_hint_max_x=80, isFieldName=True)
    self.value_field = SidebarText(text=self.format_text(field_value))
    self.app = App.get_running_app()
    self.add_widget(self.name_field)
    self.add_widget(self.value_field)

  def editable_field(self, text):
    self.remove_widget(self.value_field)
    self.value_field = EditField(text=text,
                                 size_hint_min_y=32,
                                 root=self.app.root)
    self.size_hint_max_y = 32
    self.add_widget(self.value_field)

  def format_text(self, text):
    return text if len(text) <= 32 else f"{text[0:29]}..."

class EditField(TextInput):
  def __init__(self, root, **kwargs):
    super(EditField, self).__init__(**kwargs)
    self.root = root
    self.keyboard = Window.request_keyboard(lambda *args : None, self)
    self.keyboard.bind(on_key_up=self.pressed_key)
    self.multiline = False

  def update_field(self):
    Store\
      .select(lambda state : state['update_thumbnail'])({'name': self.text})

  def pressed_key(self, *args):
    if ((13, 'enter') in args):
      self.update_field()

class SidebarPreview(ButtonBehavior, Image):
  def __init__(self, **kwargs):
    super(SidebarPreview, self).__init__(**kwargs)
    self.bind(on_press=self.double_press_checker)
    self.last_press = 1

  def double_press_checker(self, *args):
    current_time = Clock.get_time()

    if (current_time - self.last_press) <= .250:
      self.open_path()
      self.last_press = 0
    else:
      self.last_press = current_time
      Clock.schedule_once(self.single_press, .250)

  def single_press(self, *args):
    if not self.last_press:
      return

    popup = ModalView(size_hint=(.9, .9))
    popup.add_widget(Image(source=self.source, size_hint=(.95, .95)))
    popup.open()

  def open_path(self, *args):
    if system() == "Windows":
        os.startfile(self.source)
    else:
        os.system(f"(nohup nautilus --gtk-no-debug=FLAGS \"{self.source}\") &")

# Create separate class for styling in vivid.kv
class SidebarText(Label):
  def __init__(self, isFieldName=False, **kwargs):
    super(SidebarText, self).__init__(**kwargs)
    self.bind(width=lambda *args: self.set_text_size(isFieldName))

  def set_text_size(self, isFieldName):
    if isFieldName:
      self.text_size = (self.width - 15, self.height)
      self.halign = 'right'
      self.valign = 'middle'
    else:
      self.text_size = (self.width, None)
