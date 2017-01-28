import json
import re

from .version import version_comp


class CKANPackage:
    def __init__(self, id, name, builds):
        self.id = id
        self.name = name
        self.builds = builds

    def get_all_versions(self):
        return sorted([CKANVersion(build["version"]) for build in self.builds], reverse=True)

    def __getattr__(self, item):
        if item in ["abstract", "license", "author", "ksp_version", "ksp_version_min", "ksp_version_max",
                    "ksp_version_strict", "resources"]:
            return self.get_build()[item]

    def __repr__(self):
        return str((self.id, self.name))

    def get_build(self, cond=None):
        return max(list(filter(cond, self.builds)), key=lambda x: CKANVersion(x["version"]))


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
        elif self.epoch == other.epoch and version_comp(self.version, other.version) == -1:
            return True
        else:
            return False

    def __gt__(self, other):
        if self.epoch > other.epoch:
            return True
        elif self.epoch == other.epoch and version_comp(self.version, other.version) == 1:
            return True
        else:
            return False

    def __eq__(self, other):
        if self.epoch == other.epoch and version_comp(self.version, other.version) == 0:
            return True
        return False

    def __str__(self):
        return self.version_string

    def __repr__(self):
        return self.version_string


class CKANCache:
    def __init__(self, instance, uuid, rebuild=False):
        self.instance = instance
        self.uuid = uuid
        self.path = self.instance.get_repo_path(uuid) / "cache.json"
        if not self.path.exists() or rebuild:
            if not self.path.parent.exists():
                self.path.parent.mkdir(parents=True)
            with self.path.open("w") as f:
                self.packages = self.instance.parse_metadata(uuid)
                f.write(json.dumps(self.packages, indent=4))
        else:
            with self.path.open("r") as f:
                self.packages = json.load(f)

    def search(self, cond):
        filtered = list(filter(cond, self.packages))
        merged = {pid: [] for pid in [package["identifier"] for package in filtered]}
        for package in filtered:
            merged[package["identifier"]].append(package)
        packages = []
        for item in merged.items():
            packages.append(
                CKANPackage(item[0], max(item[1], key=lambda build: CKANVersion(build["version"]))["name"],
                            item[1]))  # Use the name of the newest CKAN package as the canonical Name
        return packages


class CKANAtom:
    def __init__(self, *kargs):
        if len(kargs) == 1:  # from a atom string
            pass
        elif len(kargs) == 3:  # from parts
            pass
