import logging
import re
import subprocess
import zipfile
from pathlib import Path

from .fs import find_by_regexp, find_by_name, is_relative_to


def download_to(url, dir, name):
    try:
        subprocess.check_call(["aria2c", url, "-d", dir, "-o", name])
    except subprocess.CalledProcessError:
        logging.error("Error downloading {}".format(url))


class SafetyException(Exception):
    pass


def deflate(path, dest):  # Will there be files other than .zip's?
    f = zipfile.ZipFile(path)
    f.extractall(path=dest)


def _install_file(src, kspdir, install_to, filters=None, dry_run=False):
    if install_to != "GameRoot":
        dest = Path(kspdir) / install_to
    else:
        dest = Path(kspdir)
    if not is_relative_to(dest, Path(kspdir)) or not dest.is_dir():
        raise SafetyException("A CKAN package is trying to traverse up the directories! Terminating.")
    if not install_to in ["GameData", "Ships", "Ships/SPH", "Ships/VAB", "Ships/@thumbs/VAB",
                          "Ships/@thumbs/SPH", "Tutorial", "Scenarios",
                          "GameRoot"]:  # According to the offical CKAN spec.
        raise SafetyException("Illegal install destination. Terminating.")
    if not dry_run:
        pass  # FIXME : Implement this.
    logging.info("Copying {src} to {dest}.".format(src=src, dest=dest))


class Filter:
    NAME = 1
    REGEXP = 2

    def __init__(self, type, pattern):
        self.type = type
        self.pattern = pattern

    def check(self, path: Path):
        if self.type == Filter.NAME:
            return path.name != self.pattern
        elif self.type == Filter.REGEXP:
            return not re.fullmatch(self.pattern, str(path))


def install(path, directives, instance):
    tmpdir = Path("/tmp/CKAN.py/") / Path(path).name
    deflate(path, str(tmpdir))
    filters = []
    for directive in directives:
        if "file" in directive:
            src = tmpdir / directive["file"]
        elif "find" in directive:  # Spec v1.4
            src = tmpdir / find_by_name(tmpdir, directive["find"])
        elif "find_regexp" in directive:  # Spec v1.10
            src = tmpdir / find_by_regexp(tmpdir, directive["find_regexp"])
        else:
            raise Exception("Unrecognized directive type(source).")
        dest = directive["install_to"]
        if "as" in directive:  # Spec v1.18
            dest = directive["install_to"] / directive["as"]
        if "filter" in directive:
            filters.append(("STRING", directive["filter"]))
        if "filter_regexp" in directive:
            filters.append(("REGEXP", directive["filter_regexp"]))
        _install_file(src, instance.kspdir, dest, filters=filters)


if __name__ == '__main__':
    pass
