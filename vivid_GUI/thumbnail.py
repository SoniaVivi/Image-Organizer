from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
import weakref

class Thumbnail(ButtonBehavior,Image):
  def __init__(self, data={}, press=None, **kwargs):
    super(Thumbnail, self).__init__(**kwargs)
    self.data = data
    self.press = press
    self.is_highlighted = False
    self.bind(on_press=self.select_image)

  def add_background(self, bind_pos=True):
    if bind_pos:
      self.bind(pos=self.on_position_change)
    self.is_highlighted = True
    with self.canvas.before:
      Color(0.41, 0.41, 0.41, 1, group="background")
      Rectangle(
                size=(self.size[0] + 20, self.size[1] + 20),
                pos=(self.pos[0] - 10, self.pos[1] - 10),
                group="background"
                )

  def remove_background(self):
    self.is_highlighted = False
    self.canvas.before.remove_group('background')

  def select_image(self, *args):
    if self.press(self.data, weakref.ref(self)):
      self.add_background()

  def on_position_change(self, *args):
    if self.is_highlighted:
      self.remove_background()
      self.add_background(False)

  def update(self, new_data):
    if not new_data:
      return
    self.data = {**self.data, **new_data}
