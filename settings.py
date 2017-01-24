import json
from pathlib import Path


class Settings:
    def __init__(self, path):
        self.path = path
        self.obj = json.load(open(self.path))

    def __getattr__(self, name):
        return self.obj[name]

    def __setattr__(self, name, value):
        if name in ["path", "obj", "kspdir"]:
            super().__setattr__(name, value)
        else:
            self.__dict__["obj"][name] = value

    def save(self):
        print(self.__dict__)
        f = open(self.path, "w")
        f.write(json.dumps(self.obj, indent=4))
        f.close()
        print("Saved to {}".format(self.path))


class Instance(Settings):
    def __init__(self, kspdir):
        self.kspdir = kspdir
        self.path = str(Path(self.kspdir) / "CKAN.py" / "settings.json")
        super().__init__(self.path)

    def get_repos_path(self, name):
        return Path(self.kspdir) / "CKAN.py" / "repos" / name


class GlobalSettings(Settings):
    def __init__(self):
        self.path = str((Path("~") / ".ckanpy.cfg").expanduser())
        super().__init__(self.path)


def get_current_instance():
    gs = GlobalSettings()
    for instance in gs.instances:
        if instance["name"] == gs.current_instance:
            return Instance(instance["path"])
