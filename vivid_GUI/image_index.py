from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from vivid.image_controller import ImageController
from vivid.database_controller import DatabaseController
from vivid.tag_controller import TagController
from .context_menu import ContextMenu
from .thumbnail import Thumbnail
from .add_tag_popup import AddTagPopup
from .remove_tag_popup import RemoveTagPopup
import weakref

class ImageIndex(GridLayout):
  img_controller = ImageController()
  db_controller = DatabaseController()
  tag_controller = TagController()
  find_many = db_controller.find_many
  find_by = db_controller.find_by
  remove = img_controller.remove
  get_last = db_controller.get_last

  def __init__(self, set_preview, rename_image, **kwargs):
    super(ImageIndex, self).__init__(**kwargs)
    self.bind(width=self.set_cols)
    self.next_id = 1
    self.set_preview = set_preview
    self.rename_image = rename_image
    self.selected = []
    self.shift = False
    self.is_right_click = None
    self.menu = None
    self.tag_popup = False
    self.scroll_pos = 1.0
    self.search = False
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
    max_size = self.db_controller.count('Image') if not self.search else\
                                                    len(self.search_results) - 1

    while (len(self.children) / self.cols) <  Window.height / 125 and\
          self.next_id <= max_size:
      self.get_images()
    self.get_images()

  def get_images(self, quantity=None):
    quantity = self.cols if not quantity else quantity
    next_id = self.next_id
    last_id = self.next_id - 1
    children = len(self.children)
    max_id = self.get_last('Image')['id'] if not self.search else\
                                                       len(self.search_results)

    if self.next_id > max_id:
      return

    if not self.search:
      query_result = self.find_many('Image', next_id, next_id + quantity)
      if len(query_result) < 1:
        query_result.append(None)

      for img_data in query_result:
        if not img_data:
          self.next_id = self.db_controller.next_id('Image', last_id)
          return self.get_images(children + self.cols - len(self.children))
        last_id = self._thumbnail_from_data(img_data)
    else:
      for i in range(next_id, next_id + quantity):
        if i >= len(self.search_results):
          break
        self._thumbnail_from_data(self.search_results[i])
        last_id = i

    self.next_id = last_id + 1

  def search_images(self, search_string, tags=False):
    self.search = True
    self.selected = []
    if not tags:
      self.search_results = self.db_controller.search('Image',
                                                      {'name': search_string}
                                                    )
    else:
      self.search_results = self.tag_controller.find(search_string.split(' '))
    self.next_id = 0

  def clear(self):
    self.clear_widgets()
    self.fill_space()

  def set_selected(self, data, clicked):
    if self.is_right_click:
      return
    self.set_preview(data)

    if not self.shift:
      [selected().remove_background() for selected in self.selected]
      self.selected = [clicked]
    elif self.shift and clicked not in self.selected:
      self.selected.append(clicked)
      self.select_many()

    return True

  def select_many(self):
    first_index = self.children.index(self.selected[0]())
    second_index = self.children.index(self.selected[-1]())
    step = -1 if first_index > second_index else 1

    for i in range(first_index, second_index, step):
      self.children[i].add_background()
      self.selected.append(weakref.ref(self.children[i]))

  def pressed_key(self, *args):
    self.shift = ((304, 'shift') in args)

  def released_key(self, *args):
    if (13, 'enter') not in args and self.shift:
      self.shift = ((304, 'shift') not in args)

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

  def _thumbnail_from_data(self, data):
    data['tags'] = self.tag_controller.all(data['id'])
    self.add_widget(Thumbnail(
                            data=data,
                            press=self.set_selected,
                            source=self.img_controller.get_thumbnail(data['id'])
                            )
                    )
    return int(data['id'])
