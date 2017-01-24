from pkg_resources import parse_version

from libckan.cache import CKANCache


def entry(args):
    instance = args.instance
    caches = [CKANCache(instance, name) for name, uri in instance.repos.items()]

    cond = lambda _: True

    if args.name:
        cond = lambda x: args.name in x["name"]
    elif args.desc:
        cond = lambda x: args.desc in x["abstract"]
    elif args.kspver:
        cond = lambda x: parse_version(args.kspver) == parse_version(x["ksp_version"])

    for cache in caches:
        for package in cache.search(cond):
            print("")
            print("Name:        ", package.name)
            print("Description: ", package.abstract)
            print("Version:     ", package.get_versions())
            print("")
