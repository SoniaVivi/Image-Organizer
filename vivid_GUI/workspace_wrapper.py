from kivy.uix.boxlayout import BoxLayout
from vivid_GUI.toolbar import Toolbar
from vivid_GUI.index_wrapper import IndexWrapper

class WorkspaceWrapper(BoxLayout):
  def __init__(self, **kwargs):
    super(WorkspaceWrapper, self).__init__(**kwargs)
    self.toolbar = Toolbar(on_add=self.on_add)
    self.index_wrapper = IndexWrapper()
    self.add_widget(self.toolbar)
    self.add_widget(self.index_wrapper)

  def on_add(self):
    self.index_wrapper.index.index.fill_space()
