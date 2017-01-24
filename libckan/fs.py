import re
from pathlib import Path


def find_by_name(path, name):
    if type(path) is str:
        path = Path(path)
    for child in path.iterdir():
        if child.name == name:
            return child
        elif child.is_dir():
            ret = find_by_name(child, name)
            if ret:
                return ret
    return None


def find_by_regexp(path, regexp):
    if type(path) is str:
        path = Path(path)
    for child in path.iterdir():
        if re.fullmatch(regexp, str(child)):
            return child
        elif child.is_dir():
            ret = find_by_regexp(child, regexp)
            if ret:
                return ret
    return None


def gen_file_list(path, filters):
    if type(path) is str:
        path = Path(path)
    files = []
    for child in path.iterdir():
        if child.is_dir() and all([filter_.check(child) for filter_ in filters]):
            files.append(gen_file_list(child, filters))
        files.append(child)
    for file in files:
        if not all([filter_.check(file) for filter_ in filters]):
            files.remove(file)
    return files


def is_relative_to(this, that):
    try:
        ret = this.relative_to(that)
    except ValueError:
        return False
    if ret:
        return True
