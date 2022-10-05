from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget


class OptionContainer(GridLayout):
    def __init__(self, label="", max_size=[150, 100], **kwargs):
        super(OptionContainer, self).__init__(**kwargs)
        self.cols = 2
        self.children_max_size = max_size
        self.size_hint_max_y = 100
        for _ in range(2):
            self.add_widget(Widget())
        self.add_widget(Label(text=label, size_hint_max_x=self.children_max_size[0]))
        self.add_widget(GridLayout(cols=1))
