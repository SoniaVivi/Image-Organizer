from .image_index import ImageIndex
from kivy.uix.scrollview import ScrollView

class ImageIndexContainer(ScrollView):
  def __init__(self, set_preview, rename_image, **kwargs):
    super(ImageIndexContainer, self).__init__(**kwargs)
    self.index = ImageIndex(set_preview=set_preview, rename_image=rename_image)
    self.add_widget(self.index)
    self.bind(on_scroll_start=self.scroll_direction)
    self.bind(on_scroll_stop=self.get_pos)
    self.always_overscroll = False
    self.overscroll_effect = False

  def scroll_direction(self, *args):
    self.scroll_start = self.scroll_y
    if not self.scroll_start:
      self.index.get_images()
    else:
      self.scrolling = True

  def get_pos(self, *args):
    if self.scroll_start <= self.scroll_y or not self.scrolling:
      self.scrolling = False
    elif 800 >= self.to_local(*args[1].pos)[1]:
      self.index.get_images()
    self.scrolling = False
