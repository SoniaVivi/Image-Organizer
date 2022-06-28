import os


def get_files(path, toplevel_only=True):
    with os.scandir(path) as entries:
        for entry in entries:
            is_subdirectory = os.path.isdir(entry.path)
            if not is_subdirectory:
                yield entry
            elif not toplevel_only and is_subdirectory:
                for nested_directory in get_files(entry.path, toplevel_only):
                    yield nested_directory
