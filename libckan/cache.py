import json
import logging
import tarfile
from urllib.parse import quote_plus

import requests


def fetch_latest_repo(instance, name):
    f = (instance.get_repos_path(name) / quote_plus(name)).open("wb")
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
    cache = []

    for member in tf.getmembers():
        if member.isreg() and member.name.endswith(".ckan"):
            obj = json.loads(tf.extractfile(member).read().decode("utf-8"))
            cache.append(obj)
    logging.info("Successfully parsed {} ckan files.".format(str(len(cache))))


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
        return filter(cond, self.entries)

    def from_tarball(self):
        path = self.instance.get_repos_path(self.name) / "cache.json"
