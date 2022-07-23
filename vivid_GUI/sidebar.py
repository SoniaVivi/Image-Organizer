from kivy.core.window import Window
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput
from kivy.app import App
from kivy.clock import Clock
from datetime import datetime, timedelta
from platform import system
import os
from vivid.config import Config
from vivid.database_controller import DatabaseController
from vivid.image_controller import ImageController
from vivid.tag_controller import TagController
from vivid_GUI.shared.select_child_behavior import SelectChildBehavior
from .store import Store


class Sidebar(BoxLayout):
    img_controller = ImageController()
    db_controller = DatabaseController()
    tag_controller = TagController()
    FIELD_NAMES = {"image_type": "Format", "created_at": "Added on"}

    def __init__(self, **kwargs):
        super(Sidebar, self).__init__(**kwargs)
        self.id = "sidebar"
        self.last_update = datetime.now()
        Store.dispatch("set_preview_image", self.set_preview)
        Store.dispatch("rename_image", self.rename_image)
        Store.dispatch("update_thumbnail", self.update_thumbnail)

    def set_preview(self, data):
        self.clear_widgets()
        self.add_widget(SidebarPreview(source=data["path"]))
        self.field_data = {}

        for attribute_name, value in data.items():
            field_name = None
            field_value = str(value)
            if attribute_name == "tags":
                field_value = ", ".join(value)

            if attribute_name in self.FIELD_NAMES:
                field_name = self.FIELD_NAMES[attribute_name]
            else:
                field_name = attribute_name.capitalize()

            self.field_data[attribute_name] = {
                "widget": SidebarField(field_name, field_value),
                "value": value,
            }
            self.add_widget(self.field_data[attribute_name]["widget"])

    def rename_image(self, thumbnail, in_database, on_disk):
        self.rename_properties = {"in_database": in_database, "on_disk": on_disk}
        self.thumbnail = thumbnail
        Store.dispatch("active_widget", "sidebar")
        self.field_data["name"]["widget"].editable_field(
            self.field_data["name"]["value"]
        )

    def update_thumbnail(self, data):
        time = datetime.now()
        if time - self.last_update < timedelta(seconds=1):
            return

        self.last_update = time
        new_path = (
            "path",
            self.thumbnail().data["path"],
        )

        if "name" in data:
            new_path = self.img_controller.rename(
                new_path[1],
                data["name"],
                self.rename_properties["on_disk"],
                self.rename_properties["in_database"],
            )
        updated_data = self.db_controller.find_by("Image", new_path)
        updated_data["tags"] = self.tag_controller.all(updated_data["id"])
        self.thumbnail().update(updated_data)
        self.set_preview(updated_data)


class SidebarField(BoxLayout):
    def __init__(self, field_name, field_value, **kwargs):
        super(SidebarField, self).__init__(**kwargs)
        self.name_field = SidebarText(
            text=self.format_text(field_name), size_hint_max_x=80, isFieldName=True
        )
        self.value_field = SidebarText(text=self.format_text(field_value))
        self.app = App.get_running_app()
        self.add_widget(self.name_field)
        self.add_widget(self.value_field)

    def editable_field(self, text):
        self.remove_widget(self.value_field)
        self.value_field = EditField(text=text, size_hint_min_y=32, root=self.app.root)
        self.size_hint_max_y = 32
        self.add_widget(self.value_field)

    def format_text(self, text):
        return text if len(text) <= 32 else f"{text[0:29]}..."


class EditField(TextInput):
    def __init__(self, root, **kwargs):
        super(EditField, self).__init__(**kwargs)
        self.root = root
        self.keyboard = Window.request_keyboard(lambda *args: None, self)
        self.keyboard.bind(on_key_up=self.pressed_key)
        self.multiline = False

    def update_field(self):
        Store.select(lambda state: state["update_thumbnail"])({"name": self.text})

    def pressed_key(self, *args):
        if (13, "enter") in args:
            self.update_field()


class SidebarPreview(ButtonBehavior, Image, SelectChildBehavior):
    def __init__(self, **kwargs):
        super(SidebarPreview, self).__init__(**kwargs)
        self.last_press = 1
        self.mipmap = True
        self.bind(
            on_press=lambda *args: self.double_press_checker(
                on_double_press=self.open_path, on_single_press=self.single_press
            )
        )

    def single_press(self, *args):
        if not self.last_press:
            return

        popup = ModalView(size_hint=(0.9, 0.9))
        popup.add_widget(Image(source=self.source, size_hint=(0.95, 0.95)))
        Store.dispatch("active_widget", "sidebar_modal")
        popup.bind(on_dismiss=lambda *args: Store.dispatch("active_widget", None))
        popup.open()

    def open_path(self, *args):
        if system() == "Windows":
            os.startfile(self.source)
        else:
            os.system(
                f"""({Config().read('sidebar', 'on_double_click')} "{self.source}") &"""
            )


# Create separate class for styling in vivid.kv
class SidebarText(Label):
    def __init__(self, isFieldName=False, **kwargs):
        super(SidebarText, self).__init__(**kwargs)
        self.bind(width=lambda *args: self.set_text_size(isFieldName))

    def set_text_size(self, isFieldName):
        if isFieldName:
            self.text_size = (self.width - 15, self.height)
            self.halign = "right"
            self.valign = "middle"
        else:
            self.text_size = (self.width, None)
