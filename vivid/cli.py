import cmd
from .image_controller import ImageController
from .database_controller import DatabaseController
from .tag_controller import TagController
import os


class CLI(cmd.Cmd):
    intro = "Type help or ? to list commands.\n"
    prompt = "(vivid) "
    controllers = {"db": None, "img": None, "tag": None}
    last_result = None

    def __init__(self, **kwargs):
        super().__init__()
        self._set_controllers(test=kwargs.get("test", False))

    def do_execute(self, arg):
        """Execute argument as sql."""
        try:
            print(self.execute(arg))
        except Exception as e:
            print(e)

    def do_display(self, arg):
        """
        Return records in table.

        Args:
            table (string): Name of table to retrieve records from. Required.
            min (integer): Minimum id of record to return. Defaults to 1.
            max (integer): Maximum id of record to return. Defaults to 11.
        """
        try:
            args = arg.split(" ")
            if len(args) == 3:
                print(self.display(args[0], begin_at=args[1], end_at=args[2]))
            else:
                print(self.display(arg))
        except Exception as e:
            print(e)

    def do_run(self, arg):
        """
        Execute a function of a controller.

        Args:
            arg (string): Must be in the following format: [db/img/tag].[function name]([arguments to be passed])
        """
        try:
            print(self.run(arg))
        except Exception as e:
            print(e)

    def do_working_directory(self, *args):
        """Print working directory"""
        print(os.getcwd())

    def execute(self, sql, *args):
        return CLI.controllers["db"].execute(sql, *args)

    def run(self, input_string):
        controller_name = input_string[: input_string.index(".")]
        remainder = input_string[input_string.index(".") :]
        code = f"self._save_result(CLI.controllers['{controller_name}']{remainder})"
        exec(code)
        return CLI.last_result

    def display(self, table, **kwargs):
        columns = CLI.controllers["db"].get_columns(table)
        begin_at = kwargs.get("begin_at", 1)
        end_at = kwargs.get("end_at", 11)
        records = CLI.controllers["db"].between(table, begin_at, end_at)
        display_string = ""

        for column in columns:
            display_string += self._format_column(column)

        for record in records:
            display_string += "\n"
            for column in columns:
                display_string += self._format_column(str(record[column]))

        return display_string

    def _set_controllers(self, test=False):
        if not CLI.controllers["db"]:
            CLI.controllers["db"] = DatabaseController(test=test)
            CLI.controllers["img"] = ImageController(
                db=CLI.controllers["db"], test=test
            )
            CLI.controllers["tag"] = TagController(db=CLI.controllers["db"], test=test)

    def _save_result(self, result):
        CLI.last_result = result

    def _format_column(self, data):
        max_length = 23
        while len(data) < max_length:
            data += " "
        if len(data) > max_length:
            data = data[: max_length - 3] + "..."
        return data + " | "


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    CLI().cmdloop()
