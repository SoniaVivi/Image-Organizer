from kivy.uix.boxlayout import BoxLayout
from .toolbar_modal import ToolbarModal
from .stats_button import StatsButton
from .toolbar_button import ToolbarButton
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label

class Toolbar(BoxLayout):
  def __init__(self, on_add, on_search, **kwargs):
    super(Toolbar, self).__init__(**kwargs)
    file_button = ToolbarButton(text="Add Images")
    stats_button = StatsButton()
    toolbar_search = ToolbarSearch(multiline=False)
    self.checkbox = CheckBox(size_hint_max=(20, 20))
    file_button.bind(on_press=lambda x: self.show_modal())
    toolbar_search.bind(on_text_validate=lambda instance, *args:
                        on_search(instance, search_tags=self.checkbox.active))
    self.add_widget(file_button)
    self.add_widget(stats_button)
    self.add_widget(Widget())
    self.add_widget(toolbar_search)

    self.add_widget(self.checkbox)
    self.add_widget(Label(text='Tags', size_hint_max=(40, 20)))
    self.modal = ToolbarModal(on_add=on_add)

  def show_modal(self):
    self.modal.reset_path()
    self.modal.open()

class ToolbarSearch(TextInput):
  pass
