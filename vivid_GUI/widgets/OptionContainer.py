from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from vivid_GUI.widgets.DynamicLabel import DynamicLabel


class OptionContainer(GridLayout):
    def __init__(self, label="", min_size=[150, 100], max_size=[150, 100], **kwargs):
        super(OptionContainer, self).__init__(**kwargs)
        self.cols = 2
        self.children_min_size = min_size
        self.children_max_size = max_size
        self.size_hint_max_y = 100
        for _ in range(2):
            self.add_widget(Widget())
        self.add_widget(
            DynamicLabel(
                text=label,
                size_hint_min_x=self.children_min_size[0],
                size_hint_max_x=self.children_max_size[0],
            )
        )
        self.add_widget(GridLayout(cols=1))
