from pathlib import Path
from vivid.filesearch import get_files


def file_exists(name, path=str(Path().absolute())):
    for f in get_files(path):
        if name == f.name:
            return True
    return False
