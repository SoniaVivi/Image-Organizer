from vivid.config import Config
from ..store import Store
from vivid_GUI.context_menu.context_menu_behavior import ContextMenuBehavior
from os.path import split as splitPath
from pathlib import PurePath
from ..context_menu.add_tag_popup import AddTagPopup
from ..context_menu.remove_tag_popup import RemoveTagPopup
from ..shared.select_behavior import SelectBehavior


class ImageIndexContextMenu(ContextMenuBehavior, SelectBehavior):
    def __init__(self, **kwargs):
        super(ImageIndexContextMenu, self).__init__(**kwargs)
        self.set_preview = Store.subscribe(self, "set_preview_image", "set_preview")
        self.active_menu_options = {}
        self.read_config()
        self.set_menu_options()
        Store.dispatch(
            "set_image_index_context_menu_children",
            lambda: (self.read_config(), self.set_menu_options()),
        )

    def set_menu_options(self):
        # [((options,), [validation])]
        self.menu_options = [
            (
                [
                    ("Add Tag", self.tag),
                    ("Remove Tag", lambda *args: self.tag(action="remove")),
                ],
                self.active_menu_options["image_tagging"],
            ),
            (
                [
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
                lambda: self.active_menu_options["image_renaming"]
                and len(self.selected) == 1,
            ),
            (
                [
                    (
                        "Update Creator",
                        lambda: self.update_metadata("creator"),
                    ),
                ],
                self.active_menu_options["creator_updating"],
            ),
            (
                [
                    (
                        "Update Source",
                        lambda: self.update_metadata("source"),
                    ),
                ],
                self.active_menu_options["source_updating"],
            ),
            (
                [
                    ("Search Hash", self.search_hash),
                ],
                lambda: len(self.selected) == 1
                and self.active_menu_options["hash_searching"],
            ),
            (
                [
                    ("Search Folder", self.search_folder),
                ],
                lambda: len(self.selected) == 1
                and self.active_menu_options["folder_searching"],
            ),
            (
                [
                    ("Remove", self.remove_image),
                ],
                self.active_menu_options["image_removing"],
            ),
            (
                [
                    (
                        "Remove and Blacklist",
                        lambda: (self.blacklist(), self.remove_image()),
                    ),
                    (
                        "Remove and Blacklist Parent Directory",
                        lambda: (self.blacklist("directory"), self.remove_image()),
                    ),
                ],
                lambda: self.active_menu_options["image_blacklisting"]
                and self.active_menu_options["image_removing"],
            ),
            (
                [
                    ("Delete", lambda *args: self.remove_image(keep_on_disk=False)),
                ],
                self.active_menu_options["image_deleting"],
            ),
            (
                [
                    (
                        "Delete and Blacklist Parent Directory",
                        lambda: (
                            self.blacklist("directory"),
                            self.remove_image(keep_on_disk=False),
                        ),
                    ),
                ],
                lambda: self.active_menu_options["image_blacklisting"]
                and self.active_menu_options["image_deleting"],
            ),
        ]

    def read_config(self):
        for key, value in Config().section_items("image_index_context_menu").items():
            self.active_menu_options[key] = value == "True"

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
