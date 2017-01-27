import logging
from pathlib import Path

import config


def add(args):
    gs = config.Settings()
    gs.instances.append({"name": args.name,
                         "path": str(Path(args.path).expanduser())})
    gs.save()


def rm(args):
    gs = config.Settings()
    if args.name in [instance["name"] for instance in gs.instances]:
        gs.instances = [instance for instance in gs.instances if instance["name"] != args.name]
        logging.info(gs.instances)
        gs.save()
    else:
        logging.error("The KSP instance specified does not exist.")


def list_ksp(_):
    gs = config.Settings()
    for instance in gs.instances:
        print(instance)


def use(args):
    gs = config.Settings()
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
