from pyclbr import Function
from .context_menu import ContextMenu


class ContextMenuBehavior:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_touch_down=self.right_click)
        self.menu = None
        self.menu_options = []  # [((options,), [validation])]

    def right_click(self, instance, touch):
        self.close_context_menu()
        if self.menu:
            self.menu.close()

        options = []

        self.is_right_click = touch.button == "right"
        if self.is_right_click and len(self.selected):
            for item_data in self.menu_options:
                if len(item_data) == 2:
                    if not item_data[1] or (
                        (callable(item_data[1]) and not item_data[1]())
                    ):
                        continue

                for item in item_data[0]:
                    options.append(item)

            self.menu = ContextMenu(options, pos=touch.pos)
            self.menu.open()

    def close_context_menu(self):
        if self.menu:
            self.menu.close()
