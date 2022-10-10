from kivy.uix.label import Label


class DynamicLabel(Label):
    def __init__(self, **kwargs):
        super(DynamicLabel, self).__init__(**kwargs)

    def on_size(self, *args):
        self.text_size = self.size
