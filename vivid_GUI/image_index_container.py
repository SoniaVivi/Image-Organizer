from .image_index import ImageIndex
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from .tag_list import TagList
from .store import Store

class ImageIndexContainer(ScrollView):
  def __init__(self, **kwargs):
    super(ImageIndexContainer, self).__init__(**kwargs)
    self.set_child()
    self.bind(on_scroll_start=self.scroll_direction)
    self.bind(on_scroll_stop=self.get_pos)
    self.always_overscroll = False
    self.overscroll_effect = False
    Window.bind(on_keyboard=self.key_handler)
    Store.dispatch('set_index', self.set_child)

  def set_child(self, name='image_index'):
    if hasattr(self, 'current_child'):
      self.current_child[0].close_context_menu()

    self.clear_widgets()
    if name == 'image_index':
      self.current_child = (ImageIndex(), 'image_index')
    elif name == 'tag_list':
      Store.unsubscribe(self.current_child[0], from_key='active_widget')
      self.current_child = (TagList(search=self.search_from_tag_list),
                            'tag_list')
    Store.dispatch('current_index_child', self.current_child[1])
    self.add_widget(self.current_child[0])

  def scroll_direction(self, obj, e, *args):
    self.scroll_start = self.scroll_y
    if e.button != 'scrollup':
      self.scrolling = False
    elif not self.scroll_start and self.current_child[1] == 'image_index':
      self.current_child[0].get_images()
    else:
      self.scrolling = True

  def get_pos(self, obj, e, *args):
    if self.scroll_start <= self.scroll_y or not self.scrolling\
      or e.button != 'scrollup':
      self.scrolling = False
    elif 800 >= self.to_local(*e.pos)[1] and\
         self.current_child[1] == 'image_index':
      self.current_child[0].get_images()
    self.scrolling = False

  def search_from_tag_list(self, tags=[]):
    self.set_child()
    Store.select(lambda state: state['search_images'])(" ".join(tags), True)
    Store.select(lambda state: state['searchbar']).text = " ".join(tags)

  def key_handler(self, *args):
    if 281 in args:
      if Store.select(lambda state: state['active_widget']) == 'workspace':
        if self.current_child[1] == 'image_index':
          for _ in range(0, int(self.height/125) - 1):
            self.current_child[0].get_images()
          self.scroll_to(self.current_child[0].children[0])

  def on_touch_down_callback(self, *args, **kwargs):
    Store.dispatch('active_widget', 'workspace')
