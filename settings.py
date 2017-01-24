import json
from pathlib import Path


class Settings:
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
        print(self.__dict__)
        f = self._path.open("w")
        f.write(json.dumps(self._obj, indent=4))
        f.close()
        print("Saved to {}".format(self._path))


class Instance(Settings):
    def __init__(self, kspdir: str):
        self.kspdir = kspdir
        super().__init__(self._get_path(kspdir))

    def get_repos_path(self, name):
        return Path(self.kspdir) / "CKAN.py" / "repos" / name

    def create(self, kspdir: str):
        self.kspdir = kspdir
        self.path = self._get_path(kspdir)
        self._obj = {
            "repos": [
                {"name": "default",
                 "uri": "https://github.com/KSP-CKAN/CKAN-meta/archive/master.tar.gz"
                 }
            ]
        }
        self.save()

    @staticmethod
    def _get_path(kspdir) -> Path:
        return Path(kspdir) / "CKAN.py" / "settings.json"


class GlobalSettings(Settings):
    def __init__(self):
        super().__init__((Path("~") / ".ckanpy.cfg").expanduser())

    def create(self, kspdir: str):
        self._obj = {
            "instances": [{"name": "Default", "path": kspdir}],
            "current_instance": "Default"
        }
        self.save()


def get_current_instance():
    gs = GlobalSettings()
    for instance in gs.instances:
        if instance["name"] == gs.current_instance:
            return Instance(instance["path"])
