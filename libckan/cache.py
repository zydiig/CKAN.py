import json

from libckan.version import CKANVersion


class CKANPackage:
    def __init__(self, id, name, builds):
        self.id = id
        self.name = name
        self.builds = builds

    def get_all_versions(self):
        return sorted([CKANVersion(build["version"]) for build in self.builds], reverse=True)

    def __getattr__(self, item):
        return self.get_build()[item]

    def __repr__(self):
        return str((self.id, self.name))

    def get_build(self, cond=None):
        return max(list(filter(cond, self.builds)), key=lambda x: CKANVersion(x["version"]))


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
