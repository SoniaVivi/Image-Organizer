from pathlib import PurePath
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from vivid.image_controller import ImageController
from vivid.database_controller import DatabaseController
from vivid.tag_controller import TagController
from vivid.config import Config
from vivid_GUI.context_menu.context_menu_behavior import ContextMenuBehavior
from .thumbnail import Thumbnail
from .context_menu.add_tag_popup import AddTagPopup
from .context_menu.remove_tag_popup import RemoveTagPopup
from .shared.select_behavior import SelectBehavior
from .store import Store
from os.path import split as splitPath


class ImageIndex(GridLayout, SelectBehavior, ContextMenuBehavior):
    img_controller = ImageController()
    db_controller = DatabaseController()
    tag_controller = TagController()
    config = Config()
    between = db_controller.between
    find_by = db_controller.find_by
    remove = img_controller.remove
    get_last = db_controller.get_last
    get_first = db_controller.get_first

    def __init__(self, **kwargs):
        super(ImageIndex, self).__init__(**kwargs)
        self.bind(width=self.set_cols)
        self.set_preview = Store.subscribe(self, "set_preview_image", "set_preview")
        self.tag_popup = False
        self.scroll_pos = 1.0
        self.sort = self.config.read("image_index", "sort")
        self.next_id = self._get_initial_id()
        self.bind(on_touch_down=self.on_touch_down_callback)
        """
    set_cols is called here as it requires instance variables initialized
    above.
    """
        self.set_cols()
        self.menu_options = [
            (
                [
                    ("Add Tag", self.tag),
                    (
                        "Update Creator",
                        lambda: self.update_metadata("creator"),
                    ),
                    (
                        "Update Source",
                        lambda: self.update_metadata("source"),
                    ),
                    ("Remove Tag", lambda *args: self.tag(action="remove")),
                    ("Remove", self.remove_image),
                    (
                        "Remove and Blacklist",
                        lambda: (self.blacklist(), self.remove_image()),
                    ),
                    (
                        "Remove and Blacklist Parent Directory",
                        lambda: (self.blacklist("directory"), self.remove_image()),
                    ),
                    ("Delete", lambda *args: self.remove_image(keep_on_disk=False)),
                    (
                        "Delete and Blacklist Parent Directory",
                        lambda: (
                            self.blacklist("directory"),
                            self.remove_image(keep_on_disk=False),
                        ),
                    ),
                ],
            ),
            (
                [
                    ("Search Hash", self.search_hash),
                    ("Search Folder", self.search_folder),
                    (
                        "Rename",
                        lambda *args: self.rename(on_disk=True, in_database=True),
                    ),
                    (
                        "Rename (disk only)",
                        lambda *args: self.rename(in_database=False, on_disk=True),
                    ),
                    (
                        "Rename (database only)",
                        lambda *args: self.rename(in_database=True, on_disk=False),
                    ),
                ],
                lambda: len(self.selected) == 1,
            ),
        ]
        Store.dispatch(
            "use_sort_from_config", lambda *args: self.use_sort_from_config()
        )
        Store.dispatch("search_images", self.search_images)
        Store.dispatch("refresh", self.clear)
        self.current_widget = Store.subscribe(self, "active_widget", "current_widget")

    def on_touch_down_callback(self, *args, **kwargs):
        if self.current_widget != "workspace":
            Store.dispatch("active_widget", "workspace")
        super().right_click(*args, **kwargs)

    def set_cols(self, obj=None, width=Window.width):
        self.cols = int((width / 250))
        self.fill_space()

    def fill_space(self):
        if self.sort == "ASC" or self.sort == "DESC":
            last_id = self.get_last("Image")["id"]
            first_id = self.get_first("Image")["id"]
            while (
                (len(self.children) / self.cols) < Window.height / 125
                and self.next_id <= last_id
                and self.next_id >= first_id
            ):
                self.get_images()
        elif self.sort == "search":
            max_size = len(self.search_results) - 1
            while (
                (len(self.children) / self.cols) < Window.height / 125
                and self.next_id <= max_size
                and self.next_id >= 0
            ):
                self.get_images()
        self.get_images()

    def clear(self):
        self.clear_widgets()
        if self.sort != "search":
            self.next_id = self._get_initial_id()
        self.fill_space()

    def get_images(self, quantity=None):
        quantity = self.cols if not quantity else quantity
        next_id = self.next_id
        children = len(self.children)
        max_id = 0
        if self.sort == "ASC" or self.sort == "DESC":
            max_id = self.get_last("Image")["id"]
        elif self.sort == "search":
            max_id = len(self.search_results) if len(self.search_results) else -1
        min_id = self.get_first("Image")["id"] if self.sort != "search" else 0

        if self.next_id > max_id or self.next_id < min_id:
            return

        if self.sort == "ASC" or self.sort == "DESC":
            self.range_sort(next_id, quantity, children)
        else:
            self.search_sort(next_id, quantity)

    def range_sort(self, next_id, quantity, children):
        last_id = next_id - 1 if self.sort == "ASC" else next_id
        if self.sort == "DESC":
            quantity = quantity * -1
        query_result = self.between("Image", next_id, next_id + quantity)
        if len(query_result) < 1:
            query_result.append(None)

        for img_data in query_result:
            if not img_data:
                self.next_id = self.db_controller.next_id(
                    "Image", last_id, self.sort == "ASC"
                )
                return self.get_images(children + self.cols - len(self.children))
            last_id = self._thumbnail_from_data(img_data)
        self.next_id = last_id + 1 if self.sort == "ASC" else last_id - 1

    def search_sort(self, next_id, quantity):
        last_id = next_id

        for i in range(last_id, last_id + quantity):
            if i >= len(self.search_results):
                break
            self._thumbnail_from_data(self.search_results[i])
            last_id = i + 1
        self.next_id = last_id

    def search_images(self, search_string=None, search_type="name"):
        self.sort = "search"
        if search_type == "tags":
            self.search_results = list(
                self.tag_controller.find(search_string.split(" "))
            )
        elif search_type == "folder":
            self.search_results = self.db_controller.search(
                "Image", {"path": search_string}
            )
        elif search_type == "name":
            self.search_results = self.db_controller.search(
                "Image", {"name": search_string}
            )
        elif search_type == "hash":
            self.search_results = self.db_controller.search(
                "Image", {"hash": search_string}
            )
        if search_type in ["tags", "folder", "hash"]:
            self.search_results.sort(key=lambda img: img["id"])
        self.next_id = 0
        self.clear()

    def search_folder(self, *args):
        if len(self.selected) == 1:
            current = self.selected[0]().data
            folder_path = splitPath(current["path"])[0]
            self.search_images(folder_path, search_type="folder")
            self._set_search_text(folder_path)

    def search_hash(self, *args):
        image_hash = self.selected[0]().data["hash"]
        self.search_images(search_string=image_hash, search_type="hash")
        self._set_search_text(image_hash)

    def use_sort_from_config(self, *args):
        self.sort = self.config.read("image_index", "sort")
        self.next_id = self._get_initial_id()
        self.clear()

    def set_selected(self, data, clicked):
        is_left_click = super().set_selected(clicked)
        if is_left_click:
            self.set_preview(data)
        return is_left_click

    def blacklist(self, blacklist_type="image"):
        textable_type = "path" if blacklist_type == "image" else "directory"
        for selected in self.each_selected():
            path = PurePath(selected.data["path"])
            if textable_type == "path":
                self.img_controller.blacklist_image(str(path), "path")
            elif textable_type == "directory":
                self.img_controller.blacklist_directory(str(path.parent))

    def tag(self, action="add", *args):
        if self.tag_popup:
            return
        self.tag_popup = True

        def close():
            self.tag_popup = False

        if action == "add":

            def add_tag_to_selected(name, *args):
                for selected in self.each_selected():
                    self.tag_controller.tag(selected.data["id"], name)
                    selected.data["tags"] = (*selected.data["tags"], *name.split(" "))
                    selected.data["tags"] = tuple(set(selected.data["tags"]))
                self.set_preview(selected.data)

            AddTagPopup(on_add=add_tag_to_selected, on_close=close).open()

        elif action == "remove":

            def remove_tags(tag_names, *args):
                for tag_name in tag_names:
                    for selected in self.each_selected():
                        self.tag_controller.remove(selected.data["id"], tag_name)

                        tags = list(selected.data["tags"])

                        if tag_name in tags:
                            tags.remove(tag_name)
                            selected.data["tags"] = tuple(tags)
                            if (
                                self.sort == "search"
                                and tag_name in self.tag_controller.last_search["find"]
                            ):
                                self.remove_widget(selected)

                self.set_preview(self.selected[-1]().data)

            tags = [tag for img in self.selected for tag in img().data["tags"]]
            RemoveTagPopup(on_remove=remove_tags, on_close=close, tags=tags).open()

    def remove_image(self, keep_on_disk=True, *args):
        for selected in self.each_selected():
            self.remove(selected.data["path"], db_only=keep_on_disk)
            self.remove_widget(selected)
        self.selected = []
        self.fill_space()
        self.set_preview()

    def rename(self, in_database, on_disk, *args):
        selected_thumbnail = self.selected[0]()

        def rename_func(new_name):
            nonlocal in_database
            nonlocal on_disk
            data = selected_thumbnail.data
            self.img_controller.rename(
                data["path"],
                new_name,
                in_db=in_database,
                on_disk=on_disk,
            )
            updated_data = self.db_controller.find_by("Image", {"id": data["id"]})
            updated_data["tags"] = self.tag_controller.all(updated_data["id"])
            selected_thumbnail.update(updated_data)
            self.set_preview(updated_data)

        Store.select(
            lambda state: state["edit_field"](
                "name", selected_thumbnail.data["name"], rename_func
            )
        )

    def update_metadata(self, attribute_name):
        def update_func(new_value):
            nonlocal attribute_name
            self.img_controller.update_metadata(
                [selected.data["id"] for selected in self.each_selected()],
                {attribute_name: new_value},
            )
            for selected in self.each_selected():
                selected.update(
                    self.db_controller.find_by("Image", {"id": selected.data["id"]})
                )
            self.set_preview(self.last_selected().data)

        Store.select(
            lambda state: state["edit_field"](
                attribute_name, self.last_selected().data[attribute_name], update_func
            )
        )

    def _set_search_text(self, text):
        Store.select(lambda state: state["searchbar"]).text = text

    def _get_initial_id(self):
        return {
            "ASC": self.get_first("Image")["id"],
            "DESC": self.get_last("Image")["id"],
        }[self.sort]

    def _thumbnail_from_data(self, data):
        data["tags"] = self.tag_controller.all(data["id"])
        self.add_widget(
            Thumbnail(
                data=data,
                press=self.set_selected,
                source=self.img_controller.get_thumbnail(data["id"]),
            )
        )
        return int(data["id"])
