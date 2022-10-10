from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.widget import Widget
from vivid_GUI.widgets.DynamicLabel import DynamicLabel


class LabeledCheckbox(GridLayout):
    def __init__(self, text, initial_value, on_press, **kwargs):
        super(LabeledCheckbox, self).__init__(**kwargs)
        self.cols = 3
        self.height = 15
        self.size_hint_max_y = 25
        self.padding = [0, 0, 5, 0]
        self.add_widget(DynamicLabel(text=text, halign="left", height=15, **kwargs))
        checkbox = CheckBox(active=initial_value, height=15)
        checkbox.bind(on_press=on_press)

        self.add_widget(checkbox)
        self.add_widget(Widget())
