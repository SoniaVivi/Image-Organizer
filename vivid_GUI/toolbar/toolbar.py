from kivy.uix.boxlayout import BoxLayout
from .toolbar_modal import ToolbarModal
from .stats_button import StatsButton
from .toolbar_button import ToolbarButton
from .preferences_button import PreferencesButton
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from ..store import Store

class Toolbar(BoxLayout):
  def __init__(self, **kwargs):
    super(Toolbar, self).__init__(**kwargs)
    self.current_index_child = Store.subscribe(self,
                                                 'current_index_child',
                                                 'current_index_child')
    self.set_child = Store.subscribe(self, 'set_index', 'set_child')
    file_button = ToolbarButton(text="Add Images")
    tag_list_button = ToolbarButton(text="Tag List")
    stats_button = StatsButton()
    toolbar_search = ToolbarSearch(multiline=False)
    self.tag_checkbox = CheckBox(size_hint_max=(20, 20), group="search")
    self.folder_checkbox = CheckBox(size_hint_max=(20, 20), group="search")

    file_button.bind(on_press=lambda x: self.show_modal())
    tag_list_button.bind(on_press=self.toggle_index)
    toolbar_search.bind(on_text_validate=self.on_search)

    self.add_widget(file_button)
    self.add_widget(tag_list_button)
    self.add_widget(stats_button)
    self.add_widget(PreferencesButton())
    self.add_widget(Widget())
    self.add_widget(toolbar_search)

    self.add_widget(self.tag_checkbox)
    self.add_widget(Label(text='Tags', size_hint_max=(40, 20)))
    self.add_widget(self.folder_checkbox)
    self.add_widget(Label(text='Folder', size_hint_max=(40, 20)))
    self.modal = ToolbarModal()
    Store.dispatch('searchbar', toolbar_search)

  def on_search(self, instance, *args):
    if self.current_index_child == 'tag_list':
      self.toggle_index()
    if len(instance.text) < 2:
      Store.state['update_sort']()
    else:
      Store.state['search_images'](instance.text,
                                     tags=self.tag_checkbox.active,
                                     folder=self.folder_checkbox.active)

  def show_modal(self):
    self.modal.reset_path()
    Store.dispatch('active_widget', 'toolbar_modal')
    self.modal.open()

  def toggle_index(self, *args):
    next_child = {'image_index': 'tag_list', 'tag_list': 'image_index'}
    self.set_child(next_child[self.current_index_child])

class ToolbarSearch(TextInput):
  def _on_focus(self, instance, value, *largs):
    if value:
      Store.dispatch('active_widget', 'searchbar')
    return super()._on_focus(instance, value, *largs)
