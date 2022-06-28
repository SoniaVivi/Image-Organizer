from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout


class AddTagPopup(ModalView):
    def __init__(self, on_add, on_close, **kwargs):
        super(AddTagPopup, self).__init__(**kwargs)
        self.size_hint_max = (200, 64)
        self.on_add = on_add
        self.on_close = on_close
        self.container = GridLayout(cols=1)
        self.text_input = TextInput(size_hint_max=(200, 32), multiline=False)
        self.add_tag = Button(size_hint_max=(200, 32), text="Add")

        self.text_input.bind(on_text_validate=self.add_tag_to_images)
        self.add_tag.bind(on_press=self.add_tag_to_images)

        self.container.add_widget(self.text_input)
        self.container.add_widget(self.add_tag)
        self.add_widget(self.container)

    def add_tag_to_images(self, *args):
        self.on_add(name=self.text_input.text)
        self.clear_widgets()
        self.dismiss()

    def dismiss(self):
        self.on_close()
        super(AddTagPopup, self).dismiss()
