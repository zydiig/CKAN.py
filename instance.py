import logging
from pathlib import Path

import settings


def add(args):
    gs = settings.GlobalSettings()
    gs.instances.append({"name": args.name,
                         "path": str(Path(args.path).expanduser())})
    gs.save()


def rm(args):
    gs = settings.GlobalSettings()
    if args.name in [instance["name"] for instance in gs.instances]:
        gs.instances = [instance for instance in gs.instances if instance["name"] != args.name]
        logging.info(gs.instances)
        gs.save()
    else:
        logging.error("The KSP instance specified does not exist.")


def list_ksp(_):
    gs = settings.GlobalSettings()
    for instance in gs.instances:
        print(instance)


def use(args):
    gs = settings.GlobalSettings()
    if args.name in [instance["name"] for instance in gs.instances]:
        gs.current_instance = args.name
        gs.save()
    else:
        logging.error("The KSP instance specified does not exist.")


actions = {
    "add": add,
    "rm": rm,
    "use": use,
    "list": list_ksp
}


def entry(args):
    actions[args.action](args)
