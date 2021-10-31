from kivy.uix.modalview import ModalView
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout

class RemoveTagPopup(ModalView):
  def __init__(self, on_remove, on_close, tags, **kwargs):
    super(RemoveTagPopup, self).__init__(**kwargs)
    self.size_hint = (.8, .8)
    self.on_remove = on_remove
    self.on_close = on_close
    wrapper = GridLayout(cols=1, size_hint=(.8, .8))
    self.container = GridLayout(cols=9)
    remove_button = Button(text='Keep above tags', size_hint_max_y=32,)
    remove_button.bind(on_press=self.remove)
    self.selected = []

    for tag in set(tags):
      tag_button = Button(text=tag, size_hint_max=(128, 128))
      tag_button.bind(on_press=self.on_press)
      self.container.add_widget(tag_button)

    self.add_widget(wrapper)
    wrapper.add_widget(self.container)
    wrapper.add_widget(remove_button)

  def dismiss(self):
    self.on_close()
    super(RemoveTagPopup, self).dismiss()

  def remove(self, *args):
    self.on_remove(self.selected)
    self.on_close()
    self.dismiss()

  def on_press(self, instance, *args):
    self.selected.append(instance.text)
    self.container.remove_widget(instance)
