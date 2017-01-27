import logging
from uuid import uuid4


def fetch_latest(args):
    if not args.name:
        repos = args.instance.repos
        for uuid, repo in repos.items():
            args.instance.fetch_repo(uuid, repo["uri"])
    else:
        args.instance.fetch_repo_by_name(args.name)


def add(args):
    uuid = str(uuid4())
    args.instance.repos[uuid] = args.uri
    args.instance.save()
    if not args.add_only:
        args.instance.fetch_repo(uuid)
        args.instance.parse_metadata(uuid)


def list_repo(args):
    for repo in args.instance.repos:
        print(repo)


def rm(args):
    if args.name in args.instance.repos:
        del args.instance.repos[args.name]
        args.instance.save()
    else:
        logging.error("Repository {} not found.".format(args.name))


actions = {
    "add": add,
    "rm": rm,
    "fetch": fetch_latest,
    "list": list_repo
}


def entry(args):
    logging.info(args)
    actions[args.action](args.instance, args)
