from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from .shared.select_child_behavior import SelectChildBehavior
import weakref


class Thumbnail(ButtonBehavior, Image, SelectChildBehavior):
    def __init__(self, data={}, **kwargs):
        super(Thumbnail, self).__init__(**kwargs)
        self.data = data
        self.highlight_size_increment = 20
        self.bind(on_press=self.select_image)

    def select_image(self, *args):
        if self.press(self.data, weakref.ref(self)):
            super().add_background()

    def update(self, new_data):
        if not new_data:
            return
        self.data = {**self.data, **new_data}
