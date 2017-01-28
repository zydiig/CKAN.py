from pprint import pprint

from pkg_resources import parse_version

from libckan.cache import CKANCache
from libckan.version import CKANAtom


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
            print("Identifier:  ", package.id)
            print("Name:        ", package.name)
            print("Author:      ", package.author)
            print("Description: ", package.abstract)
            print("License:     ", package.license)
            print("Versions:    ", package.get_all_versions())
            print("Resources:   ")
            pprint(package.resources)
            print("")


def resolve(args):
    atom = CKANAtom(args.atom)
    results = []
    for cache in [CKANCache(args.instance, name) for name, uri in args.instance.repos.items()]:
        results.append(atom.find_build(cache))
    pprint(results)
