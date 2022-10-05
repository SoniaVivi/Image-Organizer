from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.widget import Widget


class LabeledCheckbox(GridLayout):
    def __init__(self, text, initial_value, on_press, **kwargs):
        super(LabeledCheckbox, self).__init__(**kwargs)
        self.cols = 3
        self.height = 25
        self.size_hint_max_y = 30
        self.padding = [42, 0, 0, 0]
        self.add_widget(
            Label(
                text=text,
                halign="left",
                height=15,
            )
        )
        checkbox = CheckBox(active=initial_value == "True", height=15)
        checkbox.bind(on_press=on_press)

        self.add_widget(checkbox)
        self.add_widget(Widget())
