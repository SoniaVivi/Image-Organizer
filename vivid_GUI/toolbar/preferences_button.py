from .toolbar_button import ToolbarButton
from ..store import Store
from .preferences_modal import PreferencesModal


class PreferencesButton(ToolbarButton):
    def __init__(self, **kwargs):
        super(PreferencesButton, self).__init__(**kwargs)
        self.text = "Preferences"
        self.update_sort = Store.subscribe(self, "use_sort_from_config", "update_sort")
        self.bind(on_press=self.show_modal)

    def show_modal(self, *args):
        modal = PreferencesModal(size_hint=(0.95, 0.95), size_hint_max_x=960)
        modal.bind(on_dismiss=self.update_sort)
        Store.dispatch("active_widget", "preferences_modal")
        modal.bind(on_dismiss=lambda *args: Store.dispatch("active_widget", None))
        modal.open()
