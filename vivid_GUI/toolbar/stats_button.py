from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from vivid_GUI.store import Store
from .toolbar_button import ToolbarButton
from vivid.database_controller import DatabaseController
from vivid.image_controller import ImageController


class StatsButton(ToolbarButton):
  db_controller = DatabaseController()

  def __init__(self, **kwargs):
    super(StatsButton, self).__init__(**kwargs)
    self.text = "Stats"
    self.bind(on_press=self.show_modal)
    self.stats = {"Images": lambda : self.db_controller.count('Image'),
                  "Tags": lambda : self.db_controller.count('Tag'),
                  "Tags on Images":
                    lambda : self.db_controller.count('ImageTag')}
    self.modal = ModalView(size_hint=(.95, .95), size_hint_max_x=900)

  def show_modal(self, *args):
    self.modal.clear_widgets()
    self.modal.add_widget(self.generate_stats())
    self.modal.open()

  def generate_stats(self):
    container = GridLayout(cols=1, size_hint=(.9, .9))

    for (stat_name, stat_getter) in self.stats.items():
      container.add_widget(self.generate_modal_row(
        [StatsLabel(text=str(stat_name), size_hint_max_x=600),
         StatsLabel(text=str(stat_getter()),
                    size_hint_max_x=400,
                    isStat=True)
         ]))
    container.add_widget(
      self.generate_modal_row(
        [Button(text="Recheck images", on_press=self.existance_check)]))
    return container

  def generate_modal_row(self, widgets):
    wrapper = BoxLayout(orientation="horizontal", size_hint_max_y=32)
    parent = BoxLayout(orientation="horizontal")

    for widget in widgets:
      parent.add_widget(widget)

    wrapper.add_widget(Widget())
    wrapper.add_widget(parent)
    wrapper.add_widget(Widget())
    return wrapper

  def existance_check(self, *args):
    ImageController().existance_check()
    Store().select(lambda state: state['refresh'])()
    self.show_modal()

class StatsLabel(Label):
  def __init__(self, isStat=False, **kwargs):
    super(StatsLabel, self).__init__(**kwargs)
    self.bind(width=lambda *args: self.set_text_size(isStat))
    self.valign = 'middle'

  def set_text_size(self, isStat):
    if isStat:
      self.text_size = (self.width, self.height)
      self.halign = 'left'
    else:
      self.halign = 'right'
      self.text_size = (self.width - 25, self.height)
