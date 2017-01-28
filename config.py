import json
import logging
import tarfile
from pathlib import Path
from uuid import uuid4

import requests


class JSONConfig:
    def __init__(self, path: Path):
        self._path = path
        self._obj = json.load(self._path.open())

    def __getattr__(self, name):
        return self._obj[name]

    def __setattr__(self, name, value):
        if name in ["_path", "_obj", "kspdir"]:
            super().__setattr__(name, value)
        else:
            self.__dict__["_obj"][name] = value

    def save(self):
        f = self._path.open("w")
        f.write(json.dumps(self._obj, indent=4))
        f.close()
        print("Saved to {}".format(self._path))


class Instance(JSONConfig):
    def __init__(self, kspdir: str):
        self.kspdir = Path(kspdir)
        if not self._get_path(kspdir).exists():
            self.create(kspdir)
            super().__init__(self._get_path(kspdir))
            self.fetch_repo_by_name("default")
        else:
            super().__init__(self._get_path(kspdir))

    def get_repo_path(self, uuid) -> Path:
        path = self.kspdir / "CKAN.py/repos" / uuid
        if not path.exists():
            path.mkdir(parents=True)
        return path

    @staticmethod
    def _get_path(kspdir) -> Path:
        if type(kspdir) is str:
            kspdir = Path(kspdir)
        return kspdir / "CKAN.py/settings.json"

    @staticmethod
    def create(kspdir: str):
        obj = {
            "repos": {
                str(uuid4()): {"name": "default",
                               "uri": "https://github.com/KSP-CKAN/CKAN-meta/archive/master.tar.gz"
                               }
            }
        }
        (Path(kspdir) / "CKAN.py").mkdir(parents=True)
        f = Instance._get_path(kspdir).open("w")
        f.write(json.dumps(obj, indent=4))
        f.close()

    def fetch_repo(self, uuid, url=None):
        url = url if url else self.repos[uuid]["uri"]
        with (self.get_repo_path(uuid) / uuid).open("wb") as f:
            f.write(requests.get(url).content)
        self.parse_metadata(uuid)

    def fetch_repo_by_name(self, name):
        try:
            uuid, repo = next(p for p in self.repos.items() if p[1]["name"] == name)
            self.fetch_repo(uuid)
        except StopIteration:
            raise Exception("Repository {} not found.".format(name))

    def parse_metadata(self, repo_uuid):
        repo_uri = self.repos[repo_uuid]
        file_path = str(self.get_repo_path(repo_uuid) / repo_uuid)
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
        repo_path = self.get_repo_path(repo_uuid)
        if not repo_path.exists():
            repo_path.mkdir(parents=True)
        logging.info("Successfully parsed {} ckan files.".format(str(len(packages))))
        return packages

    def add_package_record(self, identifier, version):
        self.kspdir

    def __repr__(self):
        return "Instance('{}')".format(str(self.kspdir))


class Settings(JSONConfig):
    def __init__(self):
        super().__init__((Path("~") / ".ckanpy.cfg").expanduser())

    @staticmethod
    def create(kspdir: str):
        default_uuid = str(uuid4())
        obj = {
            "instances": {default_uuid: {"name": "Default", "path": kspdir}},
            "current_instance": default_uuid
        }
        with (Path("~") / ".ckanpy.cfg").expanduser().open("w") as f:
            f.write(json.dumps(obj, indent=4))

    def get_instance_by_name(self, name):
        try:
            return Instance(
                next(instance for uuid, instance in self.instances.items() if instance["name"] == name)["path"])
        except StopIteration:
            raise Exception("Instance lookup failed.")


def get_current_instance():
    gs = Settings()
    return Instance(gs.instances[gs.current_instance]["path"])
