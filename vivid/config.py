from configparser import ConfigParser
from os.path import isfile


class Config:
    DEFAULTS = (
        (
            "image_index",
            {"sort": "ASC"},
        ),
        (
            "image_index_context_menu",
            {
                "image_tagging": True,
                "image_renaming": True,
                "image_removing": True,
                "image_deleting": False,
                "image_blacklisting": False,
                "creator_updating": True,
                "source_updating": True,
                "folder_searching": True,
                "hash_searching": True,
            },
        ),
        ("general", {"logging": False}),
        ("sidebar", {"on_double_click": "nohup nautilus --gtk-no-debug=FLAGS"}),
    )

    def __init__(self, path="./config"):
        if not isfile(path):
            with open(path, "a+"):
                pass
        self.path = path
        self._setup()

    def set(self, section, attribute, value):
        parser = ConfigParser()
        parser.read(self.path)
        parser[section][attribute] = value
        with open(self.path, "w") as configfile:
            parser.write(configfile)

    def read(self, section, attribute):
        parser = ConfigParser()
        parser.read(self.path)
        return parser[section][attribute]

    def section_attributes(self, section):
        return [
            key for key in next(x for x in self.DEFAULTS if x[0] == section)[1].keys()
        ]

    def section_items(self, section):
        parser = ConfigParser()
        parser.read(self.path)
        items = {}
        for key in self.section_attributes(section):
            items[key] = parser[section][key]
        return items

    def _setup(self):
        parser = ConfigParser()
        parser.read(self.path)
        for section_data in Config.DEFAULTS:
            if section_data[0] not in parser:
                parser[section_data[0]] = section_data[1]
            for attribute_name, value in section_data[1].items():
                if attribute_name not in parser[section_data[0]]:
                    parser[section_data[0]][attribute_name] = value
        with open(self.path, "w") as configfile:
            parser.write(configfile)
