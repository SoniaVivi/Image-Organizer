from kivy.uix.modalview import ModalView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from .toolbar_button import ToolbarButton
from vivid.database_controller import DatabaseController

class StatsButton(ToolbarButton):
  db_controller = DatabaseController()

  def __init__(self, **kwargs):
    super(StatsButton, self).__init__(**kwargs)
    self.text = "Stats"
    self.bind(on_press=self.show_modal)
    self.stats = {"Images": lambda : self.db_controller.count('Image')}

  def show_modal(self, *args):
    modal = ModalView(size_hint=(.95, .95), size_hint_max_x=400)
    modal.add_widget(self.generate_stats())
    modal.open()

  def generate_stats(self):
    container = GridLayout(cols=1, size_hint=(.9, .9))

    for (stat_name, stat_getter) in self.stats.items():
      wrapper = BoxLayout(orientation="horizontal", size_hint_max_y=32)

      parent = BoxLayout(orientation="horizontal")
      parent.add_widget(Label(text=str(stat_name), size_hint_max_x=200))
      parent.add_widget(Label(text=str(stat_getter()), size_hint_max_x=200))

      wrapper.add_widget(Widget())
      wrapper.add_widget(parent)
      wrapper.add_widget(Widget())

      container.add_widget(wrapper)

    return container
