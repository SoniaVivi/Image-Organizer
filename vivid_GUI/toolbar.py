from kivy.uix.stacklayout import StackLayout
from .toolbar_modal import ToolbarModal
from .stats_button import StatsButton
from .toolbar_button import ToolbarButton

class Toolbar(StackLayout):
  def __init__(self, on_add, **kwargs):
    super(Toolbar, self).__init__(**kwargs)
    file_button = ToolbarButton(text="Add Images")
    stats_button = StatsButton()
    file_button.bind(on_press=lambda x: self.show_modal())
    self.add_widget(file_button)
    self.add_widget(stats_button)
    self.modal = ToolbarModal(on_add=on_add)

  def show_modal(self):
    self.modal.reset_path()
    self.modal.open()
