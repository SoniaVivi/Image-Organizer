from kivy.graphics import Color, Rectangle
from kivy.clock import Clock


class SelectChildBehavior:
    def __init__(self, press=None, **kwargs):
        self.press = press
        self.is_highlighted = False
        self.last_press = 1

    def add_background(self, bind_pos=True):
        if bind_pos:
            self.bind(pos=self.on_position_change)
        self.is_highlighted = True
        with self.canvas.before:
            Color(0.41, 0.41, 0.41, 1, group="background")
            Rectangle(
                size=(
                    self.size[0] + self.highlight_size_increment,
                    self.size[1] + self.highlight_size_increment,
                ),
                pos=(self.pos[0] - 10, self.pos[1] - 10),
                group="background",
            )

    def remove_background(self):
        self.is_highlighted = False
        self.canvas.before.remove_group("background")

    def on_position_change(self, *args):
        if self.is_highlighted:
            self.remove_background()
            self.add_background(False)

    def double_press_checker(self, on_single_press=None, on_double_press=None, *args):
        current_time = Clock.get_time()

        if (current_time - self.last_press) <= 0.250:
            on_double_press()
            self.last_press = 0
        else:
            if on_single_press:
                Clock.schedule_once(on_single_press, 0.250)
            self.last_press = current_time
