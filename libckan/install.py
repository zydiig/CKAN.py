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
    data = fpath.open("rb").read()
    ret_sha1 = True
    ret_sha256 = True
    if "sha1" in digests:
        ret_sha1 = get_sha1(data) == digests["sha1"]
    if "sha256" in digests:
        ret_sha256 = get_sha256(data) == digests["sha256"]
    return ret_sha1 and ret_sha256


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


def install(path, directives, instance, dry_run=False, overwrite=False):
    tmpdir = Path("/tmp/CKAN.py/") / path.stem
    extract(path, str(tmpdir))
    filters = []
    print(directives)
    for directive in directives:
        if "file" in directive:
            src = tmpdir / directive["file"]
        elif "find" in directive:  # Spec v1.4
            src = tmpdir / find_by_name(tmpdir, directive["find"])
        elif "find_regexp" in directive:  # Spec v1.10
            src = tmpdir / find_by_regexp(tmpdir, directive["find_regexp"])
        else:
            raise Exception("Unrecognized directive type(source).")
        if "optional" in directive and directive["optional"]:
            opt = input('The install item "{}" is optional.Would you like to install it? (Y/n) '.format(src))
            if not opt in ["yes", "Yes", "y", "Y"]:
                print("Declined: {}".format(src))
                continue
            else:
                print("Accepted: {}".format(src))
        dest = instance.kspdir if directive["install_to"] == "GameRoot" else instance.kspdir / directive[
            "install_to"]
        dest /= src.name
        if not is_relative_to(dest, instance.kspdir) or not dest.parent.is_dir():
            raise SafetyException("Attempting to write to {}".format(dest))
        if not directive["install_to"] in ["GameData", "Ships", "Ships/SPH", "Ships/VAB", "Ships/@thumbs/VAB",
                                           "Ships/@thumbs/SPH", "Tutorial", "Scenarios",
                                           "GameRoot"]:  # According to the offical CKAN spec.
            raise SafetyException("Illegal install destination.")
        if "as" in directive:
            dest = dest.with_name(directive["as"])
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
        # TODO : find_matches_files (Spec v1.16)
        records = []
        for file in gen_file_list(src, filters=filters):
            if (dest / file).is_file() and (dest / file).exists():
                raise Exception("File existed: {}".format(str(dest / file)))
            if (src / file).is_dir() and not (dest / file).exists():
                if not dry_run:
                    (dest / file).mkdir(parents=True)
                print("Created directory: ", dest / file)
            elif (src / file).is_file():
                if not dry_run:
                    shutil.copy(str(src / file), str(dest / file))
                    records.append((dest / file).relative_to(instance.kspdir))
                print("{src} -> {dest}".format(src=src, dest=dest))



def install_package(instance, build, dry_run):
    pprint(build)
    path = download_to(build["download"], "/tmp/CKAN.py/fetch", get_filename(build["download"]),
                       build["download_hash"])
    install(path, build["install"], instance, dry_run)


def dep_resolve(instance, atoms):
    pass
