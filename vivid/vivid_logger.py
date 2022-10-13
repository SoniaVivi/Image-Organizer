from datetime import datetime


class VividLogger:
    dt = datetime
    # { tag_name: { message_name: { message: str, level: int } } }
    tags = {}
    # { tag_name: [ [timestamp, message] ]}
    history = {}
    print_mode = "history"
    TEXT_STYLE_COLOR = ["0;37", "0;32", "0;33", "0;31", "1;31"]
    LEVELS = ["debug", "info", "warning", "error", "critical"]

    def __init__(self, tag):
        self._set_tag(tag)
        self.refresh_all()

    def register(self, name, message, **kwargs):
        level = kwargs.get("level", 2)

        VividLogger.tags[self.tag][name] = {
            "message": message,
            "level": level,
        }

        self.refresh(name)

    def refresh_all(self):
        for name in VividLogger.tags[self.tag]:
            self.refresh(name)

    def refresh(self, name):
        data = VividLogger.tags[self.tag][name]
        data["name"] = name

        setattr(
            self, name, lambda *args: self.write(data["message"], data["level"], *args)
        )

    def write(self, message, level, *text_args):
        message = "[\033[%sm %s \033[0;0m] [ %s ] %s" % (
            VividLogger.TEXT_STYLE_COLOR[level],
            VividLogger.LEVELS[level].upper(),
            self.tag,
            message % text_args,
        )
        time = self.dt.now().strftime("%Y-%m-%d %H:%M:%S")
        VividLogger.history[self.tag].append([time, message])
        if VividLogger.print_mode == "console":
            print(message)

    def print_history(self):
        for message_data in VividLogger.history[self.tag]:
            print(f"{message_data[0]} | {message_data[1]}")

    @classmethod
    def set_print_mode(cls, mode):
        VividLogger.print_mode = mode

    def _set_tag(self, tag):
        if tag not in VividLogger.tags:
            VividLogger.tags[tag] = {}
            VividLogger.history[tag] = []
        self.tag = tag
