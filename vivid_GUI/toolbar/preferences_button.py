from kivy.uix.modalview import ModalView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from .toolbar_button import ToolbarButton
from vivid.config import Config
from ..store import Store

class PreferencesButton(ToolbarButton):
  def __init__(self, **kwargs):
    super(PreferencesButton, self).__init__(**kwargs)
    self.text = "Preferences"
    self.update_sort = Store().subscribe(self, 'update_sort', 'update_sort')
    self.bind(on_press=self.show_modal)

  def show_modal(self, *args):
    modal = PreferencesModal(size_hint=(.95, .95), size_hint_max_x=960)
    modal.bind(on_dismiss=self.update_sort)
    modal.open()

class PreferencesModal(ModalView):
  config = Config()

  def __init__(self, **kwargs):
    super(PreferencesModal, self).__init__(**kwargs)
    self.current_sort = Config().read('image_index', 'sort')
    self.wrapper = GridLayout(cols=3)
    self.max_size = [150, 300]
    self.sort_attribute()
    self.add_widget(self.wrapper)

  def sort_attribute(self):
    container = GridLayout(cols=2, size_hint_max_y=100)
    for _ in range(2): container.add_widget(Widget())
    container.add_widget(
                    Label(text='Sort Order', size_hint_max_x=self.max_size[0]))

    buttons_container = GridLayout(cols=1)
    for sort in ['ASC', 'DESC']:
      padding_top = 15
      wrapper = GridLayout(rows=2, cols=2, size_hint_max_x=150, size_hint_min_y=35)
      checkbox = CheckBox(group='sort',
                          active=sort == self.current_sort)

      checkbox.bind(on_press=self.set_sort)
      for _ in range(2): wrapper.add_widget(Widget(size_hint_min_y=padding_top))
      wrapper.add_widget(checkbox)
      wrapper.add_widget(Label(text=self.get_sort_text(sort)))
      buttons_container.add_widget(wrapper)
    container.add_widget(buttons_container)

    self.wrapper.add_widget(container)
  def get_sort_text(self, text):
    return {'ASC': 'First Added',
            'First Added': 'ASC',
            'DESC': 'Last Added',
            'Last Added': 'DESC',
           }[text]

  def set_sort(self, widget):
    self.config.set('image_index',
                    'sort',
                    self.get_sort_text(widget.parent.children[0].text)
                   )

