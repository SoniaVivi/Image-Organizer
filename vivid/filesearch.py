import os
from pathlib import Path


def get_files(path, toplevel_only=True):
    for entry in Path(path).iterdir():
        if not entry.is_dir():
            yield entry
        elif not toplevel_only and entry.is_dir():
            for nested_directory in get_files(str(entry), toplevel_only):
                yield nested_directory
