from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button

class ContextMenu(FloatLayout):
  def __init__(self, items, pos, **kwargs):
    super(ContextMenu, self).__init__(**kwargs)
    self.window = Window
    self.items = items
    self.pos = self.pos[0], self.pos[1] - self.size[1]


  def add_children(self):
    x, y = self.window.mouse_pos

    for i, item in enumerate(self.items):
      self.add_widget(ContextItem(text=item[0],
                                  on_press=item[1],
                                  pos=(x + 12, y - 20 - i * 32),
                                  close=self.close
                                  ))

  def open(self):
    self.add_children()
    self.window.add_widget(self)

  def close(self):
    self.window.remove_widget(self)

class ContextItem(Button):
  def __init__(self, on_press=None, close=None, **kwargs):
    super(ContextItem, self).__init__(**kwargs)
    self.press = on_press
    self.close = close
    self.bind(on_press=self.on_press)

  def on_press(self, *args):
    self.press()
    self.close()
