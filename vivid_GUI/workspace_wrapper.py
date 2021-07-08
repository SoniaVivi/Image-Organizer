from kivy.uix.boxlayout import BoxLayout
from vivid_GUI.toolbar import Toolbar
from vivid_GUI.index_wrapper import IndexWrapper

class WorkspaceWrapper(BoxLayout):
  def __init__(self, **kwargs):
    super(WorkspaceWrapper, self).__init__(**kwargs)
    self.toolbar = Toolbar(on_add=self.on_add, on_search=self.on_search)
    self.index_wrapper = IndexWrapper()
    self.add_widget(self.toolbar)
    self.add_widget(self.index_wrapper)

  def on_add(self):
    self.index_wrapper.index.index.fill_space()

  def on_search(self, instance, search_tags=False, *args):
    if len(instance.text) < 2 and not search_tags:
      self.index_wrapper.index.index.search = False
      self.index_wrapper.index.index.next_id = 1
    else:
      self.index_wrapper.index.index.search_images(instance.text,
                                                   tags=search_tags)

    self.index_wrapper.index.index.clear()
