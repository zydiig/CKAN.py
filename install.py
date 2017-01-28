from libckan import install as _install
from libckan.cache import CKANCache


def install(args):
    instance = args.instance
    caches = [CKANCache(instance, name) for name, uri in instance.repos.items()]
    cond = lambda x: x["identifier"] in args.id
    results = []
    for cache in caches:
        results += cache.search(cond)
    if len(results) > 1:
        for idx, pkg in enumerate(results):
            print("[{}]".format(idx), pkg.name)
        indices = [int(ns) for ns in input("Which to install (Space seperated indices):").split(" ")]
        results = [result for idx, result in enumerate(results) if idx in indices]
    for pkg in results:
        _install.install_package(instance, pkg.get_build(), dry_run=args.dry_run)


def remove(args):
    pass
