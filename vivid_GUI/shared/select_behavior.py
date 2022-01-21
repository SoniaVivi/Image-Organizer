from kivy.core.window import Window
import weakref

class SelectBehavior():
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.selected = []
    self.pressed_keys = {'shift': False, 'ctrl': False}
    self.keyboard = Window.request_keyboard(lambda *args : None, self)
    self.keyboard.bind(on_key_down=self.pressed_key,
                       on_key_up=self.released_key
                      )
    self.is_right_click = None

  def set_selected(self, clicked, **kwargs):
    self.on_ctrl_reclick = kwargs.get('on_ctrl_reclick', self._deselect)
    if self.is_right_click:
      return

    if True not in list(map(lambda x: x[1], self.pressed_keys.items())):
      [img().remove_background() for img in self.selected if img() is not None]
      self.selected = [clicked]
    elif clicked in self.selected:
      if self.pressed_keys['ctrl']:
        self.on_ctrl_reclick(clicked)
      return
    elif self.pressed_keys['shift'] and len(self.selected) > 0:
      self.selected.append(clicked)
      self.select_many()
    elif self.pressed_keys['ctrl']:
      self.selected.append(clicked)
    return True

  def select_many(self):
    first_index = self.children.index(self.selected[-2]())
    second_index = self.children.index(self.selected[-1]())
    step = -1 if first_index > second_index else 1

    for i in range(first_index, second_index, step):
      self.children[i].add_background()
      self.selected.append(weakref.ref(self.children[i]))

  def pressed_key(self, *args):
    self.pressed_keys['shift'] = (304, 'shift') in args
    self.pressed_keys['ctrl'] = (305, 'lctrl') in args or (306, 'rctrl') in args

  def released_key(self, *args):
    if (13, 'enter') not in args:
      if self.pressed_keys['shift']:
        self.pressed_keys['shift'] = (304, 'shift') not in args
      if self.pressed_keys['ctrl']:
        self.pressed_keys['ctrl'] = (305, 'lctrl') not in args and\
                                    (306, 'rctrl') not in args
  def each_selected(self):
    for selected in self.selected:
      yield selected()

  def _deselect(self, clicked):
    clicked().remove_background()
    self.selected = [x for x in self.selected if x != clicked]
