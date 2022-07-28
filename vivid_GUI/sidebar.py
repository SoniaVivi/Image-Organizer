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
        Store.dispatch("set_preview_image", self.set_preview)
        Store.dispatch("edit_field", self.edit_field)

    def set_preview(self, data=None):
        self.clear_widgets()
        if not data:
            return
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

    def edit_field(self, attribute_name, initial_text, modification_function):
        Store.dispatch("active_widget", "sidebar")
        self.field_data[attribute_name]["widget"].editable_field(
            initial_text, modification_function
        )


class SidebarField(BoxLayout):
    def __init__(self, field_name, field_value, **kwargs):
        super(SidebarField, self).__init__(**kwargs)
        self.name_field = SidebarText(
            full_text=field_name, size_hint_max_x=80, isFieldName=True
        )
        self.value_field = SidebarText(full_text=field_value)
        self.app = App.get_running_app()
        self.add_widget(self.name_field)
        self.add_widget(self.value_field)

    def editable_field(self, text, update_func):
        self.remove_widget(self.value_field)
        self.value_field = EditField(
            text=str(text),
            size_hint_min_y=32,
            root=self.app.root,
            update_field=update_func,
        )
        self.size_hint_max_y = 32
        self.add_widget(self.value_field)


class EditField(TextInput):
    def __init__(self, root, update_field, **kwargs):
        super(EditField, self).__init__(**kwargs)
        self.root = root
        self.keyboard = Window.request_keyboard(lambda *args: None, self)
        self.keyboard.bind(on_key_up=self.pressed_key)
        self.multiline = False
        self.update_field = update_field
        self.last_update = datetime.now()
        self.enter_count = 0
        self.initial_text = self.text

    def pressed_key(self, *args):
        # Kivy frequently registers keys to be pressed 2+ times causing the function
        # to be fired multiple times. First with the intended text and then with the initial text.
        if (13, "enter") in args and self.initial_text != self.text:
            time = datetime.now()
            if time - self.last_update < timedelta(seconds=1) or self.enter_count >= 1:
                return
            self.last_update = datetime.now()
            self.enter_count += 1
            self.update_field(self.text)


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
    def __init__(self, isFieldName=False, full_text="", **kwargs):
        super(SidebarText, self).__init__(**kwargs)
        self.full_text = full_text
        self.bind(width=lambda *args: self.set_text_size(isFieldName))

    def set_text_size(self, isFieldName):
        if isFieldName:
            self.text_size = (self.width - 15, self.height)
            self.halign = "right"
            self.valign = "middle"
            self.text = self.full_text
        else:
            self.text_size = (self.width, None)
            self.text = self.trim_text()

    def trim_text(self):
        text = self.full_text
        return (
            text if len(text) <= 32 else f"{text[0:int((self.parent.width / 12))]}..."
        )
