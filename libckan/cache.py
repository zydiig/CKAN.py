import json
import logging
import re
import tarfile
from urllib.parse import quote_plus

import requests

from .version import version_comp


def fetch_latest_repo(instance, name):
    f = (instance.get_repos_path(name) / quote_plus(instance.repos[name])).open("wb")
    f.write(requests.get(instance.repos[name]).content)
    f.close()


def parse_metadata(instance, repo_name):
    repo = instance.repos[repo_name]
    file_path = str(instance.get_repos_path(repo_name) / quote_plus(repo))
    try:
        tf = tarfile.open(file_path)
    except IOError:
        logging.error("File {} not found.".format(file_path))
        return
    packages = []
    for member in tf.getmembers():
        if member.isreg() and member.name.endswith(".ckan"):
            package = json.loads(tf.extractfile(member).read().decode("utf-8"))
            packages.append(package)
    # packages_merged={package_id:[] for package_id in set([package["identifier"] for package in packages])}
    # for package in packages:
    #     packages_merged[package["identifier"]].append(package)
    f = open(str(instance.get_repos_path(repo_name) / "cache.json"), "w")
    f.write(json.dumps(packages, indent=4))
    f.close()
    logging.info("Successfully parsed {} ckan files.".format(str(len(packages))))


class Package:
    def __init__(self, id, name, builds):
        self.id = id
        self.name = name
        self.builds = builds

    def get_versions(self):
        return sorted([CKANVersion(build["version"]) for build in self.builds], reverse=True)

    def __getattr__(self, item):
        if item in ["abstract"]:
            return max(self.builds, key=lambda x: CKANVersion(x["version"]))[item]


class CKANVersion:
    def __init__(self, version_string):
        self.version_string = version_string
        match = re.match(r"((\d+):)?(.+)", version_string)
        if not match.group(2):
            self.epoch = 0
        else:
            self.epoch = int(match.group(2))
        self.version = match.group(3)

    def __lt__(self, other):
        if self.epoch < other.epoch:
            return True
        if version_comp(self.version, other.version) == -1:
            return True
        return False

    def __gt__(self, other):
        if self.epoch > other.epoch:
            return True
        if version_comp(self.version, other.version) == 1:
            return True
        return False

    def __eq__(self, other):
        if self.epoch == other.epoch and self.version == other.version:
            return True
        return False

    def __str__(self):
        return self.version_string

    def __repr__(self):
        return self.version_string


class CKANCache:
    def __init__(self, instance, repo_name, rebuild=False):
        self.instance = instance
        self.name = repo_name
        self.path = self.instance.get_repos_path(repo_name) / "cache.json"
        f = self.path.open()
        if rebuild:
            parse_metadata(self.instance, repo_name)
        else:
            self.entries = json.load(f)

    def search(self, cond):
        filtered = list(filter(cond, self.entries))
        merged = {pid: [] for pid in [package["identifier"] for package in filtered]}
        for package in filtered:
            merged[package["identifier"]].append(package)
        packages = []
        for item in merged.items():
            packages.append(
                Package(item[0], max(item[1], key=lambda build: CKANVersion(build["version"]))["name"], item[1]))
        return packages
