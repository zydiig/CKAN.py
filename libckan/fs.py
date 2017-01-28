import logging
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


def gen_file_list(path: Path, filters=None, toplevel=True):
    filters = filters or []
    files = [] if toplevel else [path]
    for child in path.iterdir():
        if all([filter_.check(child) for filter_ in filters]):
            if child.is_dir():
                files += gen_file_list(child, filters, toplevel=False)
            else:
                files.append(child)
    files = [file.relative_to(path) for file in files] if toplevel else files
    for file in files:
        if not all([filter_.check(file) for filter_ in filters]):
            files.remove(file)
            logging.info("Filtered:{}".format(file))
    return files


def is_relative_to(this, that):
    try:
        this.relative_to(that)
    except ValueError:
        return False
    else:
        return True
