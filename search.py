from pkg_resources import parse_version

import settings
from libckan.cache import CKANCache


def entry(args):
    instance = settings.get_current_instance()
    caches = [CKANCache(instance, name) for name, uri in instance.repos.items()]
    if args.name:
        def cond(x):
            if args.name in x["name"]:
                return True
            return False
    elif args.desc:
        def cond(x):
            if args.desc in x["abstract"]:
                return True
            return False
    elif args.kspver:
        def cond(x):
            if parse_version(args.kspver) == parse_version(x["ksp_version"]):
                return True
            return False

    def cond(x):
        return True

    for cache in caches:
        print(cache.search(cond))
