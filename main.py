from kivy.config import Config

from vivid.image_controller import ImageController

Config.set("input", "mouse", "mouse,multitouch_on_demand")
# If set to below 1000, shifts hightlighted thumbnails on right click
# Setting it to 1000 or above then resizing lower manually has it work normally
Config.set("graphics", "width", "1080")
Config.set("kivy", "default_font", ["Lato", "./fonts/Lato-Regular.ttf"])

import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from kivy.app import App
from kivy.uix.widget import Widget
from vivid_GUI import sidebar
from vivid_GUI.image_index.image_index_container import ImageIndexContainer
from vivid_GUI.toolbar.toolbar import Toolbar
from vivid.file_exists import file_exists
from vivid.database_controller import DatabaseController
from vivid.config import Config as VividConfig
from vivid.vivid_logger import VividLogger as Logger
import os
import re

DatabaseController.read_config()


class Workspace(Widget):
    def __init__(self, **kwargs):
        super(Workspace, self).__init__(**kwargs)


class VividApp(App):
    def build(self):
        self._set_image_controller_plugins()
        return Workspace()

    def _set_image_controller_plugins(self):
        config = VividConfig()
        for (plugin_name, value) in config.section_items("plugins").items():
            if value == "False":
                continue
            get_trailing = "(?<=^(%s)).*"
            if re.search(get_trailing % ("add_image_",), plugin_name) is not None:
                stem = re.search(get_trailing % ("add_image_",), plugin_name)[0]
                ImageController.add_middleware(
                    "add_image", path=f"vivid_GUI/plugins/add_image/{stem}.py"
                )
                logger = Logger("Workspace")
                logger.write(
                    f"#_set_image_controller_plugins: added middleware from {stem}.py",
                    1,
                )


def delete_nohup():
    if file_exists("nohup.out"):
        os.remove("nohup.out")


delete_nohup()

if __name__ == "__main__":
    VividApp().run()
