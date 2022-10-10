from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.widget import Widget
from vivid_GUI.widgets.DynamicLabel import DynamicLabel


class LabeledRadio(GridLayout):
    def __init__(self, group, active, on_press, text, **kwargs):
        super(LabeledRadio, self).__init__(**kwargs)
        padding_top = 15
        self.rows = 2
        self.cols = 2
        self.size_hint_max_x = 150
        self.size_hint_min_y = 35
        checkbox = CheckBox(group=group, active=active)
        checkbox.bind(on_press=on_press)
        for _ in range(2):
            self.add_widget(Widget(size_hint_min_y=padding_top))
        self.add_widget(checkbox)
        self.add_widget(DynamicLabel(text=text))
