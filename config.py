import json
from pathlib import Path
from uuid import uuid4


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
        self.kspdir = kspdir
        super().__init__(self._get_path(kspdir))

    def get_repos_path(self, name):
        return Path(self.kspdir) / "CKAN.py" / "repos" / name

    def create(self, kspdir: str):
        self.kspdir = kspdir
        self.path = self._get_path(kspdir)
        self._obj = {
            "repos": {
                str(uuid4()): {"name": "default",
                               "uri": "https://github.com/KSP-CKAN/CKAN-meta/archive/master.tar.gz"
                               }
            }
        }
        self.save()

    def fetch_repos(self, ):
        pass

    @staticmethod
    def _get_path(kspdir) -> Path:
        return Path(kspdir) / "CKAN.py" / "settings.json"


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
        f = (Path("~") / ".ckanpy.cfg").expanduser().open("w")
        f.write(json.dumps(obj, indent=4))
        f.close()


def get_current_instance():
    gs = Settings()
    return next(Instance(instance["path"]) for instance in gs.instances if instance["name"] == gs.current_instance)
