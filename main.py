from kivy.config import Config

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
import os

DatabaseController.read_config()


class Workspace(Widget):
    def __init__(self, **kwargs):
        super(Workspace, self).__init__(**kwargs)


class VividApp(App):
    def build(self):
        return Workspace()


def delete_nohup():
    if file_exists("nohup.out"):
        os.remove("nohup.out")


delete_nohup()

if __name__ == "__main__":
    VividApp().run()
