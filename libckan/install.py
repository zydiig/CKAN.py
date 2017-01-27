import logging
import shutil
import subprocess
import zipfile
from pathlib import Path
from pprint import pprint

from .fs import find_by_regexp, find_by_name, is_relative_to, gen_file_list
from .structures import Filter
from .utils import get_filename, get_sha1, get_sha256


def check_digests(fpath, digests):
    if len(digests.keys()) != 2:
        raise Exception("Digests incomplete.")
    data = fpath.open("rb").read()
    if get_sha1(data) == digests["sha1"] and get_sha256(data) == digests["sha256"]:
        return True
    else:
        return False


def download_to(url, dir, name, digests=None):
    dir = str(dir) if type(dir) is Path else dir
    fpath = Path(dir) / name
    print(fpath)
    if fpath.exists() and digests:
        if check_digests(fpath, digests):
            return fpath
    try:
        subprocess.check_call(["aria2c", url, "-d", dir, "-o", name, "--allow-overwrite"])
    except subprocess.CalledProcessError:
        logging.error("Error downloading {}".format(url))
        return None
    if digests:
        if not check_digests(fpath, digests):
            raise Exception("Digest verification failed.")
    return fpath


class SafetyException(Exception):
    pass


def extract(path: Path, dest):  # Will there be files other than .zip's?
    logging.info(("Extracting to ", dest))
    if not path.exists():
        path.mkdir(parents=True)
    f = zipfile.ZipFile(str(path))
    f.extractall(path=dest)


def _install_file(src: Path, kspdir: str, install_to: str, dry_run=False):
    if install_to != "GameRoot":
        dest = Path(kspdir) / install_to
    else:
        dest = Path(kspdir)
    if not is_relative_to(dest, Path(kspdir)) or not dest.is_dir():
        logging.error(str(dest))
        raise SafetyException("A CKAN package is trying to traverse up the directories! Terminating.")
    if not install_to in ["GameData", "Ships", "Ships/SPH", "Ships/VAB", "Ships/@thumbs/VAB",
                          "Ships/@thumbs/SPH", "Tutorial", "Scenarios",
                          "GameRoot"]:  # According to the offical CKAN spec.
        raise SafetyException("Illegal install destination. Terminating.")
    if not dry_run:
        shutil.copy(str(src), str(dest))
    logging.info("Copying {src} to {dest}.".format(src=src, dest=dest))


def install(path, directives, instance, dry_run=False):
    tmpdir = Path("/tmp/CKAN.py/") / path.stem
    extract(path, str(tmpdir))
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
        rename = False
        if "as" in directive:  # Spec v1.18
            dest = directive["install_to"]
            rename = True
            as_ = directive["as"]
        if "filter" in directive:
            if type(directive["filter"]) is list:
                filters += [Filter(Filter.NAME, filter_string) for filter_string in directive["filter"]]
            else:
                filters.append(Filter(Filter.NAME, directive["filter"]))
        if "filter_regexp" in directive:
            if type(directive["filter_regexp"]) is list:
                filters += [Filter(Filter.REGEXP, filter_string) for filter_string in directive["filter_regexp"]]
            else:
                filters.append(Filter(Filter.REGEXP, directive["filter_regexp"]))
        # FIXME : find_matches_files (v1.16)
        for file in gen_file_list(tmpdir, filters=filters):
            print(file)
            if (tmpdir / file).is_dir():
                (dest / file).mkdir(parents=True)
            elif (tmpdir / file).is_file():
                _install_file(src, instance.kspdir, dest, dry_run)
        if rename and not dry_run:
            shutil.move(str(dest / (src.relative_to(tmpdir))), str(dest / as_))


def install_package(instance, ckan_metadata, dry_run):
    pprint(ckan_metadata)
    path = download_to(ckan_metadata["download"], "/tmp/CKAN.py/fetch", get_filename(ckan_metadata["download"]),
                       ckan_metadata["download_hash"])
    install(path, ckan_metadata["install"], instance, dry_run)


if __name__ == '__main__':
    pass
