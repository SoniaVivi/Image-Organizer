from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from vivid_GUI.store import Store
from .toolbar_button import ToolbarButton
from vivid.database_controller import DatabaseController
from vivid.image_controller import ImageController


class StatsButton(ToolbarButton):
    db_controller = DatabaseController()
    img = ImageController()

    def __init__(self, **kwargs):
        super(StatsButton, self).__init__(**kwargs)
        self.text = "Stats"
        self.bind(on_press=self.show_modal)
        self.stats = {
            "Images": lambda: self.db_controller.count("Image"),
            "Tags": lambda: self.db_controller.count("Tag"),
            "Tags on Images": lambda: self.db_controller.count("ImageTag"),
        }
        self.modal = ModalView(size_hint=(0.95, 0.95), size_hint_max_x=900)

    def show_modal(self, *args):
        self.modal.clear_widgets()
        self.modal.add_widget(self.create_children())
        Store.dispatch("active_widget", "stats_modal")
        self.modal.bind(on_dismiss=lambda *args: Store.dispatch("active_widget", None))
        self.modal.open()

    def create_children(self):
        container = GridLayout(cols=1, size_hint=(0.9, 0.9))

        for (stat_name, stat_getter) in self.stats.items():
            container.add_widget(
                self.generate_modal_row(
                    [
                        StatsLabel(text=str(stat_name), size_hint_max_x=600),
                        StatsLabel(
                            text=str(stat_getter()), size_hint_max_x=400, isStat=True
                        ),
                    ]
                )
            )
        [container.add_widget(row) for row in self._create_action_buttons()]
        return container

    def generate_modal_row(self, widgets):
        wrapper = BoxLayout(orientation="horizontal", size_hint_max_y=32)
        parent = BoxLayout(orientation="horizontal")

        for widget in widgets:
            parent.add_widget(widget)

        wrapper.add_widget(Widget())
        wrapper.add_widget(parent)
        wrapper.add_widget(Widget())
        return wrapper

    def existence_check(self, *args):
        self.img.existence_check()
        Store.select(lambda state: state["refresh"])()
        self.show_modal()

    def recreate_thumbnails(self, *args):
        self.img.recreate_thumbnails()
        Store.select(lambda state: state["refresh"])()
        self.show_modal()

    def _create_action_buttons(self):
        return [
            self.generate_modal_row(
                [Button(text="Recheck images", on_press=self.existence_check)]
            ),
            self.generate_modal_row(
                [Button(text="Recreate Thumbnails", on_press=self.recreate_thumbnails)]
            ),
        ]


class StatsLabel(Label):
    def __init__(self, isStat=False, **kwargs):
        super(StatsLabel, self).__init__(**kwargs)
        self.bind(width=lambda *args: self.set_text_size(isStat))
        self.valign = "middle"

    def set_text_size(self, isStat):
        if isStat:
            self.text_size = (self.width, self.height)
            self.halign = "left"
        else:
            self.halign = "right"
            self.text_size = (self.width - 25, self.height)
