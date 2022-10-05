from kivy.uix.modalview import ModalView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from vivid.database_controller import DatabaseController
from vivid.image_controller import DatabaseController
from kivy.uix.textinput import TextInput
from vivid.config import Config
from vivid_GUI.widgets.LabeledCheckbox import LabeledCheckbox
from ..store import Store
from ..widgets.LabeledRadio import LabeledRadio
from ..widgets.OptionContainer import OptionContainer


class PreferencesModal(ModalView):
    config = Config()

    def __init__(self, **kwargs):
        super(PreferencesModal, self).__init__(**kwargs)
        self.current_sort = Config().read("image_index", "sort")
        self.logging_value = Config().read("general", "logging")
        self.sidebar_on_double_click = Config().read("sidebar", "on_double_click")
        self.wrapper = GridLayout(cols=3)
        self.max_size = [150, 100]
        self.wrapper.add_widget(self.create_sort_option())
        self.wrapper.add_widget(self.create_logging_option())
        self.wrapper.add_widget(Widget())
        [self.wrapper.add_widget(Widget(size_hint_max_y=60)) for _ in range(3)]
        sidebar_widgets = self.create_sidebar_on_double_click_option()
        self.wrapper.add_widget(sidebar_widgets[0])
        self.wrapper.add_widget(sidebar_widgets[1])
        self.wrapper.add_widget(Widget())
        self.wrapper.add_widget(
            self._create_section_header("Image Index Context Menu Actions")
        )
        [
            self.wrapper.add_widget((Widget(size_hint_max_y=45, size_hint_min_y=45)))
            for _ in range(2)
        ]
        [self.wrapper.add_widget(x) for x in self.create_context_menu_options()]
        [self.wrapper.add_widget(Widget()) for _ in range(3)]
        self.add_widget(self.wrapper)

    def _create_section_header(self, text):
        temp = GridLayout(cols=1, padding=[-5, 0, 0, 0])
        temp.add_widget(
            Label(
                text=text,
                halign="left",
            )
        )
        return temp

    def create_sort_option(self):
        container = OptionContainer(label="Sort Order")
        buttons_container = container.children[0]

        for sort in ["ASC", "DESC"]:
            buttons_container.add_widget(
                LabeledRadio(
                    "sort",
                    sort == self.current_sort,
                    self.set_sort,
                    self.get_sort_text(sort),
                )
            )
        return container

    def create_logging_option(self):
        container = OptionContainer(label="Logging")
        buttons_container = container.children[0]
        for text in ["True", "False"]:
            buttons_container.add_widget(
                LabeledRadio(
                    "logging",
                    text == self.logging_value,
                    self.set_logging,
                    self.get_logging_text(text),
                )
            )
        return container

    def create_sidebar_on_double_click_option(self):
        container = OptionContainer(
            label="Run command on double click",
        )
        container.padding = (120, 0)
        text_box = TextInput(text=self.sidebar_on_double_click, multiline=False)
        text_box.size_hint_max_y = 30
        text_box.bind(
            on_text_validate=lambda widget: Config().set(
                "sidebar", "on_double_click", widget.text
            )
        )
        return [container, text_box]

    def create_context_menu_options(self):
        widgets = []
        for name, value in Config().section_items("image_index_context_menu").items():
            widgets.append(
                LabeledCheckbox(
                    self.get_context_menu_text(name),
                    value,
                    lambda widget, x=name: (
                        Config().set("image_index_context_menu", x, str(widget.active)),
                        Store.select(
                            lambda state: state[
                                "set_image_index_context_menu_children"
                            ]()
                        ),
                    ),
                )
            )
        return widgets

    def set_logging(self, widget):
        self.config.set(
            "general",
            "logging",
            self.get_logging_text(widget.parent.children[0].text),
        )
        DatabaseController.read_config()

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

    def get_context_menu_text(self, attribute):
        return attribute[0].upper() + " ".join(attribute.split("_"))[1:]

    def set_sort(self, widget):
        self.config.set(
            "image_index", "sort", self.get_sort_text(widget.parent.children[0].text)
        )
