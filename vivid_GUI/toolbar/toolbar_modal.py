from kivy.uix.filechooser import  FileChooserIconView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from vivid.image_controller import ImageController
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from vivid_GUI.store import Store
from os.path import expanduser
import re

class ToolbarModal(ModalView):
  img_controller = ImageController()

  def __init__(self, **kwargs):
    super(ToolbarModal, self).__init__(**kwargs)
    self.size_hint=(.8, .8)
    container = BoxLayout(size_hint=(1, 1), orientation="vertical")
    self.file_chooser = FileChooserIconView(
                                              dirselect=True,
                                              multiselect=True
                                            )
    self.file_options = FileOptions(options=['Only Unique',
                                             'Scramble Names',
                                             'Use Hash As Name'])
    container.add_widget(self.file_options )
    container.add_widget(self.file_chooser)
    container.add_widget(
                    Button(
                           text="Add",
                           size_hint_max_x=100,
                           size_hint_max_y=32, on_press=lambda x: self.add_file()
                           )
                    )
    self.add_widget(container)
    self.file_chooser.bind(on_entries_cleared=self.clear_selection)
    self.on_add = Store().subscribe(self, 'refresh', 'on_add')

  def add_file(self):
    options = self.file_options.get_selected()
    options = {'unique': options['only_unique'],
               'hash_as_name': options['use_hash_as_name'],
               'scramble_name': options['scramble_names']}

    if len(self.file_chooser.selection):
      for path in self.file_chooser.selection:
        self.img_controller.add(path, **options)
    else:
      self.img_controller.add(self.file_chooser.path)
    self.file_chooser.selection = []
    self.on_add()
    self.dismiss()

  def clear_selection(self, *args):
    self.file_chooser.selection = []

  def reset_path(self):
    self.file_chooser.path = expanduser('~/Pictures')

class FileOptions(GridLayout):
  def __init__(self, options=[], **kwargs):
    super(FileOptions, self).__init__(**kwargs)
    self.rows = 1
    self.row_default_height = 36
    self.col_default_width = 154
    self.spacing = (10, 0)
    self.padding = (55, 5)
    [self.add_option(option) for option in options]

  def add_option(self, text):
    wrapper = GridLayout(cols=2, size_hint_max_x=154)
    wrapper.add_widget(Label(text=text, height=38))
    wrapper.add_widget(CheckBox(height=38))
    self.add_widget(wrapper)

  def get_selected(self):
    selected = {}
    for child in self.children:
      selected[re.sub(r'\s', "_", child.children[-1].text.lower())] = child.children[-2].active
    return selected
