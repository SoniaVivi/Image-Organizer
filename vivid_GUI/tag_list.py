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
    self.search = search
    self.display()
    self.bind(on_touch_down = self.right_click)
    self.menu = None

  def set_cols(self, obj=None, width=None):
    width = self.width if width is None else width
    self.canvas.before.remove_group('divider')
    self.cols=int((width / 125) - 1)
    if self.cols:
      self.set_dividers(width / self.cols)

  def display(self):
    tags = self.db.find_many('Tag',
                              self.db.get_first('Tag')['id'],
                              self.db.get_last('Tag')['id'] + 1,
                            )
    tags.sort(key=lambda tag: tag['name'])
    for i, tag in enumerate(tags):
      self.add_widget(TagListChild(color=self.col_color,
                                   text=tag['name'],
                                   press=super().set_selected,
                                   double_press=self.search,
                                   set_row_height=self.set_row_height,
                                   position=i + 1))

  def set_dividers(self, col_width):
    self.canvas.before.remove_group('divider')

    for n in range(1, self.cols):
      with self.canvas.before:
        x_offset = (n * col_width + 1)
        Color(*self.col_color, group="divider", mode='rgb')
        Line(points=(x_offset, 0, x_offset, self.height),
             # width=1.0 occasionally produces lines with distorted colors
             # width=1.5 produces lines that are too thick.
             width=1.01,
             group="divider"
             )

  # Does not recalc when window is resized thus resulting in misaligned borders
  def set_row_height(self, child_position, height):
    if child_position == 0 or self.cols == 0 or not self.cols:
      return
    self.children[-1].set_border()

    row = int((child_position - 1) / self.cols)
    if (row not in self.rows_minimum or self.rows_minimum[row] < height):
      self.rows_minimum = self.rows_minimum | {row: height}
      self.reset_child_borders(row)

  def reset_child_borders(self, row):
    [child.set_border() for child in self.children]
    row_height = self.rows_minimum[row]

    for i in range((row * self.cols) - 1, (row * self.cols) + 1):
      self.children[-i].set_border(row_height)

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
  def __init__(self, color, press, double_press, set_row_height, position, **kwargs):
    super(TagListChild, self).__init__(**kwargs)
    self.bind(on_press=lambda *args:
                self.on_press_callback(lambda : double_press([self.text])))
    self.bind(width=lambda *args: self.set_border())
    self.bind(height=lambda *args: self.set_border())
    self.col_color = color
    self.press = press
    self.bind(on_press=self.select)
    self.highlight_size_increment = 10
    self.bind(texture_size=lambda *args:
                self.height_callback(set_row_height, position, *args))

  def set_border(self, row_height=None):
    self.canvas.before.remove_group('border')
    offset = 0

    with self.canvas.before:
      Color(*self.col_color, mode="rgb")
      Line(width=1,
           points=(self.x,
                   self.y + offset,
                   self.x + self.width,
                   self.y + offset),
           group="border")
      if row_height:
        self.text_size = (self.width, row_height + 10)

  def select(self, *args):
    if self.press(weakref.ref(self)):
      super().add_background()

  def on_press_callback(self, on_double_press):
    self.double_press_checker(self.select, on_double_press)

  def height_callback(self, set_height, position, texture=None, *args):
    if texture:
      self.height = max([(((len(self.text) / 18) + 1) * 18), 32])
      self.text_size = (self.width, self.height)
      set_height(position, self.height)
