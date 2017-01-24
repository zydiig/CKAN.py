import logging

from libckan import cache


def fetch_latest(instance, args):
    repos = instance.repos
    if not args.repo_name:
        for repo in repos.items():
            cache.fetch_latest_repo(instance, repo)
    else:
        cache.fetch_latest_repo(instance, args.name)


def add(instance, args):
    instance.repos[args.name] = args.uri
    instance.save()
    if not args.add_only:
        cache.fetch_latest_repo(instance, args.name)
        cache.parse_metadata(instance, args.name)


def list_repo(instance, _):
    for repo in instance.repos:
        print(repo)


def rm(instance, args):
    if args.name in instance.repos:
        del instance.repos[args.name]
        instance.save()
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
