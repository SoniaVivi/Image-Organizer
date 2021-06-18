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
from platform import system
import os

class Sidebar(BoxLayout):
  def __init__(self, img_data=None, **kwargs):
    super(Sidebar, self).__init__(**kwargs)
    self.img_data = img_data if img_data else self.empty_data()
    self.id = 'sidebar'
    self.update_children()

  def empty_data(self):
    return {'name': '', 'path': '', 'hash': '', 'image_type': ''}

  def update_children(self):
    self.clear_widgets()
    field_data = [
                  ("Name", self.img_data['name']),
                  ("Path", self.img_data['path']),
                  ("Hash", self.img_data['hash']),
                  ("Format", self.img_data['image_type'])
                 ]
    self.add_widget(SidebarPreview(source=self.img_data['path']))
    for data in field_data:
      self.add_widget(SidebarField(data[0], data[1]))

  def rename(self):
    self.children[3].editable_field(self.img_data['name'])

class SidebarField(BoxLayout):
  def __init__(self, field_name, field_value, **kwargs):
    super(SidebarField, self).__init__(**kwargs)
    self.name_field = SidebarText(text=self.format_text(field_name),
                            size_hint_max_x=80)
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
    self.root.children[0].index_wrapper.update_thumbnail({'name': self.text})

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

class SidebarText(Label):
  pass
