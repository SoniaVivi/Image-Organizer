from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from vivid.database_controller import DatabaseController
from kivy.graphics import Color, Line
from .shared.select_behavior import SelectBehavior
from .shared.select_child_behavior import SelectChildBehavior
from .context_menu.context_menu import ContextMenu
import weakref

class TagList(GridLayout, SelectBehavior):
  db = DatabaseController()

  def __init__(self, search, **kwargs):
    super(TagList, self).__init__(**kwargs)
    self.bind(width=self.set_cols)
    self.bind(height=lambda object, *args: self.set_cols(object))
    self.last_id = 0
    self.col_color = (64/255, 158/255, 1,)
    self.display()
    self.search = search
    self.bind(on_touch_down = self.right_click)
    self.menu = None

  def set_cols(self, obj=None, width=None):
    width = self.width if width is None else width
    self.canvas.before.remove_group('divider')
    self.cols=int((width / 145) - 1)
    if self.cols:
      self.set_dividers(width / self.cols)

  def display(self):
    tags = self.db.find_many('Tag',
                              self.db.get_first('Tag')['id'],
                              self.db.get_last('Tag')['id'],
                            )
    tags.sort(key=lambda tag: tag['name'])
    for tag in tags:
      self.add_widget(TagListChild(color=self.col_color,
                                   text=tag['name'],
                                   press=super().set_selected))

  def set_dividers(self, col_width):
    self.canvas.before.remove_group('divider')

    for n in range(1, self.cols):
      with self.canvas.before:
        x_offset = (n * col_width)
        Color(*self.col_color, group="divider", mode='rgb')
        Line(points=(x_offset, 0, x_offset, self.height),
             # width=1.0 occasionally produces lines with distorted colors
             # width=1.5 produces lines that are too thick.
             width=1.01,
             group="divider"
             )

  def right_click(self, instance, touch):
    if self.menu:
      self.menu.close()

    self.is_right_click = touch.button == 'right'
    if self.is_right_click and len(self.selected):
      menu_options = [
                      ("Search Tags", self.search_tags),
                     ]

      self.menu = ContextMenu(menu_options, pos=touch.pos)
      self.menu.open()

  def search_tags(self):
    self.search([tag().text for tag in self.selected])

class TagListChild(ButtonBehavior, Label, SelectChildBehavior):
  def __init__(self, color, press, **kwargs):
    super(TagListChild, self).__init__(**kwargs)
    self.bind(on_press=self.select)
    self.bind(width=self.set_border)
    self.col_color = color
    self.press = press
    self.bind(on_press=self.select)
    self.highlight_size_increment = 10

  def set_border(self, *args):
    with self.canvas.before:
      Color(*self.col_color, mode="rgb")
      Line(width=1, points=(self.x, self.y, self.x + self.width, self.y))

  def select(self, *args):
    if self.press(weakref.ref(self)):
      super().add_background()

