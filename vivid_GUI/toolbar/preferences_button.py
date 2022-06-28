from kivy.uix.modalview import ModalView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from vivid.image_controller import ImageController
from .toolbar_button import ToolbarButton
from vivid.config import Config
from ..store import Store


class PreferencesButton(ToolbarButton):
    def __init__(self, **kwargs):
        super(PreferencesButton, self).__init__(**kwargs)
        self.text = "Preferences"
        self.update_sort = Store.subscribe(self, "use_sort_from_config", "update_sort")
        self.bind(on_press=self.show_modal)

    def show_modal(self, *args):
        modal = PreferencesModal(size_hint=(0.95, 0.95), size_hint_max_x=960)
        modal.bind(on_dismiss=self.update_sort)
        Store.dispatch("active_widget", "preferences_modal")
        modal.bind(on_dismiss=lambda *args: Store.dispatch("active_widget", None))
        modal.open()


class PreferencesModal(ModalView):
    config = Config()

    def __init__(self, **kwargs):
        super(PreferencesModal, self).__init__(**kwargs)
        self.current_sort = Config().read("image_index", "sort")
        self.logging_value = Config().read("image_controller", "logging")
        self.wrapper = GridLayout(cols=3)
        self.max_size = [150, 300]
        self.wrapper.add_widget(self.create_sort_option())
        self.wrapper.add_widget(self.create_logging_option())
        self.add_widget(self.wrapper)

    def create_sort_option(self):
        container = self._create_option_container(label="Sort Order")
        buttons_container = container.children[0]

        for sort in ["ASC", "DESC"]:
            buttons_container.add_widget(
                self._create_labeled_radio(
                    "sort",
                    sort == self.current_sort,
                    self.set_sort,
                    self.get_sort_text(sort),
                )
            )
        return container

    def create_logging_option(self):
        container = self._create_option_container(label="Logging")
        buttons_container = container.children[0]
        for text in ["True", "False"]:
            buttons_container.add_widget(
                self._create_labeled_radio(
                    "logging",
                    text == self.logging_value,
                    self.set_logging,
                    self.get_logging_text(text),
                )
            )
        return container

    def set_logging(self, widget):
        self.config.set(
            "image_controller",
            "logging",
            self.get_logging_text(widget.parent.children[0].text),
        )
        ImageController.read_config()

    def get_logging_text(self, text):
        return {
            "True": "Enable",
            "False": "Disable",
            "Enable": "True",
            "Disable": "False",
        }[text]

    def get_sort_text(self, text):
        return {
            "ASC": "First Added",
            "First Added": "ASC",
            "DESC": "Last Added",
            "Last Added": "DESC",
        }[text]

    def set_sort(self, widget):
        self.config.set(
            "image_index", "sort", self.get_sort_text(widget.parent.children[0].text)
        )

    def _create_option_container(self, label=""):
        container = GridLayout(cols=2, size_hint_max_y=100)
        for _ in range(2):
            container.add_widget(Widget())
        container.add_widget(Label(text=label, size_hint_max_x=self.max_size[0]))
        container.add_widget(GridLayout(cols=1))
        return container

    def _create_labeled_radio(self, group, active, on_press, text):
        padding_top = 15
        wrapper = GridLayout(rows=2, cols=2, size_hint_max_x=150, size_hint_min_y=35)
        checkbox = CheckBox(group=group, active=active)
        checkbox.bind(on_press=on_press)
        for _ in range(2):
            wrapper.add_widget(Widget(size_hint_min_y=padding_top))
        wrapper.add_widget(checkbox)
        wrapper.add_widget(Label(text=text))
        return wrapper
