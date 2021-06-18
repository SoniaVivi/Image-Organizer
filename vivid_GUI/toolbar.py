from kivy.uix.stacklayout import StackLayout
from kivy.uix.button import Button
from .toolbar_modal import ToolbarModal

class Toolbar(StackLayout):
  def __init__(self, on_add, **kwargs):
    super(Toolbar, self).__init__(**kwargs)
    file_button = ToolbarButton(text="Add Images")
    file_button.bind(on_press=lambda x: self.show_modal())
    self.add_widget(file_button)
    self.modal = ToolbarModal(on_add=on_add)

  def show_modal(self):
    self.modal.reset_path()
    self.modal.open()

class ToolbarButton(Button): # Create separate class for styling in kvlang
  pass

