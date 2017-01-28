from libckan import install as _install
from libckan.cache import CKANCache


def install(args):
    instance = args.instance
    caches = [CKANCache(instance, name) for name, uri in instance.repos.items()]
    cond = lambda x: x["identifier"] in args.id
    results = []
    for cache in caches:
        results += cache.search(cond)
    for pkg in results:
        _install.install_package(instance, pkg.get_build(), dry_run=True)


def remove(args):
    pass
