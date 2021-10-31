from kivy.uix.filechooser import  FileChooserIconView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from vivid.image_controller import ImageController
from kivy.uix.button import Button
from os.path import expanduser

class ToolbarModal(ModalView):
  img_controller = ImageController()

  def __init__(self, on_add, **kwargs):
    super(ToolbarModal, self).__init__(**kwargs)
    self.size_hint=(.8, .8)
    container = BoxLayout(size_hint=(1, 1), orientation="vertical")
    self.file_chooser = FileChooserIconView(
                                              dirselect=True,
                                              multiselect=True
                                            )
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
    self.on_add = on_add

  def add_file(self):
    if len(self.file_chooser.selection):
      for path in self.file_chooser.selection:
        self.img_controller.add(path)
    else:
      self.img_controller.add(self.file_chooser.path)
    self.file_chooser.selection = []
    self.dismiss()
    self.on_add()

  def clear_selection(self, *args):
    self.file_chooser.selection = []

  def reset_path(self):
    self.file_chooser.path = expanduser('~/Pictures')
