import logging

from libckan import cache
from settings import get_current_instance


def fetch_latest(args):
    instance = get_current_instance()
    repos = instance.repos
    if not args.repo_name:
        for repo in repos.items():
            cache.fetch_latest_repo(instance, repo)
    else:
        cache.fetch_latest_repo(instance, args.name)


def add(args):
    instance = get_current_instance()
    instance.repos[args.name] = args.uri
    instance.save()
    if not args.add_only:
        cache.fetch_latest_repo(instance, args.name)


def list_repo(args):
    instance = get_current_instance()
    for repo in instance.repos:
        print(repo)


def rm(args):
    ins_settings = get_current_instance()
    if args.name in ins_settings.repos:
        del ins_settings.repos[args.name]
        ins_settings.save()
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
    actions[args.action](args)
