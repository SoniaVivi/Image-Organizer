from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from vivid.image_controller import ImageController
from vivid.database_controller import DatabaseController
from vivid.tag_controller import TagController
from vivid.config import Config
from .context_menu import ContextMenu
from .thumbnail import Thumbnail
from .add_tag_popup import AddTagPopup
from .remove_tag_popup import RemoveTagPopup
import weakref

class ImageIndex(GridLayout):
  img_controller = ImageController()
  db_controller = DatabaseController()
  tag_controller = TagController()
  config = Config()
  find_many = db_controller.find_many
  find_by = db_controller.find_by
  remove = img_controller.remove
  get_last = db_controller.get_last
  get_first = db_controller.get_first

  def __init__(self, set_preview, rename_image, **kwargs):
    super(ImageIndex, self).__init__(**kwargs)
    self.bind(width=self.set_cols)
    self.set_preview = set_preview
    self.rename_image = rename_image
    self.selected = []
    self.pressed_keys = {'shift': False, 'ctrl': False}
    self.is_right_click = None
    self.menu = None
    self.tag_popup = False
    self.scroll_pos = 1.0
    self.sort = self.config.read('image_index', 'sort')
    self.next_id = self._get_initial_id()
    self.keyboard = Window.request_keyboard(lambda *args : None, self)
    self.keyboard.bind(on_key_down=self.pressed_key,
                       on_key_up=self.released_key
                      )
    self.bind(on_touch_down = self.right_click)
    self.set_cols()
    self.fill_space()

  def set_cols(self, obj=None, width=Window.width):
    self.cols=int((width / 250))
    self.fill_space()

  def fill_space(self):
    max_size = 0
    if self.sort == 'ASC' or self.sort == 'DESC':
      max_size = self.get_last('Image')['id']
    elif self.sort == 'search':
      max_size = len(self.search_results) - 1

    while (len(self.children) / self.cols) <  Window.height / 125 and\
          self.next_id <= max_size and\
          self.next_id >= self.get_first('Image')['id']:
      self.get_images()
    self.get_images()

  def get_images(self, quantity=None):
    quantity = self.cols if not quantity else quantity
    next_id = self.next_id
    children = len(self.children)
    max_id = 0
    if self.sort == 'ASC' or self.sort == 'DESC':
      max_id = self.get_last('Image')['id']
    elif self.sort == 'search':
      max_id = len(self.search_results)
    min_id = self.get_first('Image')['id']

    if self.next_id > max_id or self.next_id < min_id:
      return

    if self.sort == 'ASC' or self.sort == 'DESC':
      self.range_sort(next_id, quantity, children)
    else:
      self.search_sort(next_id, quantity)

  def range_sort(self, next_id, quantity, children):
    last_id = next_id - 1 if self.sort == 'ASC' else next_id
    if self.sort == 'DESC':
      quantity = quantity * -1
    query_result = self.find_many('Image',
                                  next_id,
                                  next_id + quantity,
                                  self.sort == 'ASC')
    if len(query_result) < 1:
      query_result.append(None)

    for img_data in query_result:
      if not img_data:
        self.next_id =\
          self.db_controller.next_id('Image', last_id, self.sort == 'ASC')
        return self.get_images(children + self.cols - len(self.children))
      last_id = self._thumbnail_from_data(img_data)
    self.next_id = last_id + 1 if self.sort == 'ASC' else last_id - 1

  def search_sort(self, next_id, quantity):
    last_id = next_id - 1

    for i in range(next_id, next_id + quantity):
      if i >= len(self.search_results):
        break
      self._thumbnail_from_data(self.search_results[i])
      last_id = i
    self.next_id = last_id + 1

  def search_images(self, search_string, tags=False):
    self.sort = 'search'
    if not tags:
      self.search_results = self.db_controller.search('Image',
                                                      {'name': search_string}
                                                    )
    else:
      self.search_results = self.tag_controller.find(search_string.split(' '))
    self.next_id = self.get_first('Image')['id']

  def clear(self):
    self.clear_widgets()
    self.fill_space()

  def update_sort(self, *args):
    self.sort = self.config.read('image_index', 'sort')
    self.next_id = self._get_initial_id()
    self.clear()

  def set_selected(self, data, clicked):
    if self.is_right_click:
      return
    self.set_preview(data)

    if True not in list(map(lambda x: x[1], self.pressed_keys.items())):
      [img().remove_background() for img in self.selected if img() is not None]
      self.selected = [clicked]
    elif clicked in self.selected:
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


  def right_click(self, instance, touch):
    if self.menu:
      self.menu.close()

    self.is_right_click = touch.button == 'right'
    if self.is_right_click and len(self.selected):
      menu_options = [
                      ("Add Tag", self.tag),
                      ("Remove Tag", lambda *args: self.tag(action="remove")),
                      ("Remove", self.remove_image),
                      ("Delete",
                          lambda *args : self.remove_image(keep_on_disk=False))
                     ]

      if len(self.selected) == 1:
        menu_options += [
                         ("Rename", lambda *args: self.rename(on_disk=True)),
                         ("Rename (disk only)",
                           lambda *args: self.rename(False, True)),
                         ("Rename (database only)", self.rename)
                        ]

      self.menu = ContextMenu(menu_options, pos=touch.pos)
      self.menu.open()

  def tag(self, action='add', *args):
    if self.tag_popup:
      return
    self.tag_popup = True

    def close():
      self.tag_popup = False

    if action == 'add':
      def add_tag_to_selected(name, *args):
        for selected in self.selected:
          self.tag_controller.tag(selected().data['id'], name)
          selected().data['tags'] = (*selected().data['tags'], name)
          selected().data['tags'] = tuple(set(selected().data['tags']))
        self.set_preview(selected().data)

      AddTagPopup(on_add=add_tag_to_selected, on_close=close).open()

    elif action == 'remove':
      def remove_tags(tag_names, *args):
        for tag_name in tag_names:
          for selected in self.selected:
            self.tag_controller.remove(selected().data['id'], tag_name)

            tags = list(selected().data['tags'])

            if tag_name in tags:
              tags.remove(tag_name)
              selected().data['tags'] = tuple(tags)

        self.set_preview(self.selected[-1]().data)

      tags = [tag for img in self.selected for tag in img().data['tags']]
      RemoveTagPopup(on_remove=remove_tags, on_close=close, tags=tags).open()

  def remove_image(self, keep_on_disk=True, *args):
    for selected in self.selected:
      self.remove(selected().data['path'], keep_on_disk)
      self.remove_widget(selected())
    self.selected = []
    self.fill_space()
    self.set_preview()

  def rename(self, in_database=True, on_disk=False):
    self.rename_image(self.selected[0], in_database, on_disk)

  def _get_initial_id(self):
    return {'ASC': self.get_first('Image')['id'],
            'DESC': self.get_last('Image')['id']}[self.sort]

  def _thumbnail_from_data(self, data):
    data['tags'] = self.tag_controller.all(data['id'])
    self.add_widget(Thumbnail(
                            data=data,
                            press=self.set_selected,
                            source=self.img_controller.get_thumbnail(data['id'])
                            )
                    )
    return int(data['id'])
