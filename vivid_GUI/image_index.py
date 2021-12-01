from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from vivid.image_controller import ImageController
from vivid.database_controller import DatabaseController
from vivid.tag_controller import TagController
from vivid.config import Config
from .context_menu.context_menu import ContextMenu
from .thumbnail import Thumbnail
from .context_menu.add_tag_popup import AddTagPopup
from .context_menu.remove_tag_popup import RemoveTagPopup
from .shared.select_behavior import SelectBehavior
from .store import Store

class ImageIndex(GridLayout, SelectBehavior):
  img_controller = ImageController()
  db_controller = DatabaseController()
  tag_controller = TagController()
  config = Config()
  find_many = db_controller.find_many
  find_by = db_controller.find_by
  remove = img_controller.remove
  get_last = db_controller.get_last
  get_first = db_controller.get_first

  def __init__(self, **kwargs):
    super(ImageIndex, self).__init__(**kwargs)
    self.bind(width=self.set_cols)
    self.set_preview = Store().subscribe(self, 'set_preview_image', 'set_preview')
    self.rename_image = Store().subscribe(self, 'rename_image', 'rename_image')
    self.menu = None
    self.tag_popup = False
    self.scroll_pos = 1.0
    self.sort = self.config.read('image_index', 'sort')
    self.next_id = self._get_initial_id()
    self.bind(on_touch_down = self.right_click)
    self.set_cols()
    self.fill_space()
    Store().dispatch("update_sort", self.update_sort)
    Store().dispatch("search_images", self.search_images)
    Store().dispatch("refresh", self.clear)

  def set_cols(self, obj=None, width=Window.width):
    self.cols=int((width / 250))
    self.fill_space()

  def fill_space(self):
    if self.sort == 'ASC' or self.sort == 'DESC':
      max_size = self.get_last('Image')['id']
      while (len(self.children) / self.cols) <  Window.height / 125 and\
            self.next_id <= max_size and\
            self.next_id >= self.get_first('Image')['id']:
        self.get_images()
    elif self.sort == 'search':
      max_size = len(self.search_results) - 1
      while (len(self.children) / self.cols) <  Window.height / 125 and\
            self.next_id <= max_size and\
            self.next_id >= 0:
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
      max_id = len(self.search_results) if len(self.search_results) else -1
    min_id = self.get_first('Image')['id'] if self.sort != 'search' else 0

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
    last_id = next_id

    for i in range(last_id, last_id + quantity):
      if i >= len(self.search_results):
        break
      self._thumbnail_from_data(self.search_results[i])
      last_id = i + 1
    self.next_id = last_id

  def search_images(self, search_string=None, tags=False, folder=False):
    self.sort = 'search'
    if tags:
      self.search_results = list(self.tag_controller.find(search_string.split(' ')))
    elif folder:
      self.search_results = self.db_controller.search('Image',
                                                      {'path': search_string})
    else:
      self.search_results = self.db_controller.search('Image',
                                                      {'name': search_string}
                                                    )
    if tags or folder:
      self.search_results.sort(key=lambda img : img['id'])
    self.next_id = 0
    self.clear()

  def clear(self):
    self.clear_widgets()
    if not self.sort:
      self.next_id = self._get_initial_id()
    self.fill_space()

  def update_sort(self, *args):
    self.sort = self.config.read('image_index', 'sort')
    self.next_id = self._get_initial_id()
    self.clear()

  def set_selected(self, data, clicked):
    is_left_click = super().set_selected(clicked)
    if is_left_click:
      self.set_preview(data)
    return is_left_click

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
          selected().data['tags'] = (*selected().data['tags'], *name.split(' '))
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
