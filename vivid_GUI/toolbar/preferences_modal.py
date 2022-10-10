from kivy.uix.modalview import ModalView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from vivid.database_controller import DatabaseController
from vivid.image_controller import DatabaseController
from kivy.uix.textinput import TextInput
from vivid.config import Config
from vivid_GUI.widgets.Header import Header
from vivid_GUI.widgets.LabeledCheckbox import LabeledCheckbox
from ..store import Store
from ..widgets.LabeledRadio import LabeledRadio
from ..widgets.OptionContainer import OptionContainer
from pathlib import Path
from vivid.config import Config


class PreferencesModal(ModalView):
    config = Config()

    def __init__(self, **kwargs):
        super(PreferencesModal, self).__init__(**kwargs)
        self.current_sort = Config().read("image_index", "sort")
        self.logging_value = Config().read("general", "logging")
        self.sidebar_on_double_click = Config().read("sidebar", "on_double_click")
        self.wrapper = GridLayout(cols=3)
        self.wrapper.padding = [50, 0, 0, 0]
        self.max_size = [150, 100]
        self.wrapper.add_widget(self.create_sort_option())
        self.wrapper.add_widget(self.create_logging_option())
        self.wrapper.add_widget(Widget())
        [self.wrapper.add_widget(Widget(size_hint_max_y=60)) for _ in range(3)]
        sidebar_widgets = self.create_sidebar_on_double_click_option()
        self.wrapper.add_widget(sidebar_widgets[0])
        self.wrapper.add_widget(sidebar_widgets[1])
        self.wrapper.add_widget(Widget())
        self.wrapper.add_widget(Header("Image Index Context Menu Actions"))
        [self.wrapper.add_widget(HeadingFiller()) for _ in range(2)]
        [self.wrapper.add_widget(x) for x in self.create_context_menu_options()]
        [self.wrapper.add_widget(x) for x in self.create_plugin_options()]
        # Add widgets above this line
        # Line below forces widgets to be descending
        [self.wrapper.add_widget(Widget()) for _ in range(3)]
        self.add_widget(self.wrapper)

    def create_plugin_options(self):
        widgets = []
        widgets.extend(
            [
                Header("Plugins: ImageController#add_image"),
                *[HeadingFiller() for _ in range(2)],
                Header(text="Any changes requires a restart to take effect"),
                *[HeadingFiller(filler_padding=25) for _ in range(2)],
            ]
        )
        for plugin_path in Path("./vivid_GUI/plugins/add_image/").iterdir():
            data = compile(
                open(
                    Path(plugin_path),
                    mode="rb",
                ).read(),
                filename=plugin_path,
                mode="exec",
            )
            plugin_data = {}
            exec(data, globals(), plugin_data)

            config = Config()
            key_name = f"add_image_{plugin_path.stem}"
            if not config.exists("plugins", key_name):
                config.set("plugins", key_name, "False")
            is_selected = config.read("plugins", key_name) == "True"

            widgets.append(
                LabeledCheckbox(
                    plugin_data["title"],
                    is_selected,
                    on_press=lambda widget, *args: config.set(
                        "plugins", key_name, str(widget.active)
                    ),
                )
            )
        return widgets

    def create_sort_option(self):
        container = OptionContainer(label="Sort Order", max_size=[75, 100])
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
        container.children[1].size_hint_max_x = 50
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
            min_size=[300, 100],
        )
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
                    value == "True",
                    lambda widget, x=name: (
                        Config().set("image_index_context_menu", x, str(widget.active)),
                        Store.select(
                            lambda state: state[
                                "set_image_index_context_menu_children"
                            ]()
                        ),
                    ),
                    size_hint_min_x=150,
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


class HeadingFiller(Widget):
    def __init__(self, filler_padding=45, **kwargs):
        super(HeadingFiller, self).__init__(**kwargs)
        self.size_hint_max_y = filler_padding
        self.size_hint_min_y = filler_padding
