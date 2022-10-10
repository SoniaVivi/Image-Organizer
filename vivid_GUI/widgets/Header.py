from kivy.uix.gridlayout import GridLayout
from vivid_GUI.widgets.DynamicLabel import DynamicLabel


class Header(GridLayout):
    def __init__(self, text, **kwargs):
        super(Header, self).__init__(**kwargs)
        self.cols = 1
        self.padding = [-5, 0, 0, 0]
        self.add_widget(
            DynamicLabel(
                text=text,
                halign="left",
            )
        )
