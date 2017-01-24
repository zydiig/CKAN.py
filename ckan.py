import argparse
import logging

import instance
import search
from libckan import repo

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

parser = argparse.ArgumentParser()
modules = {"instance": instance, "repo": repo}
subparsers = parser.add_subparsers(help="Modules to invoke.")

repo_parser = subparsers.add_parser('repo', help='Repository management')
repo_parser.add_argument("action", choices=repo.actions.keys())
repo_parser.add_argument("name", help="Name of the repository.", nargs="?")
repo_parser.add_argument("uri", help="URI of the repository.", nargs="?")
repo_parser.add_argument("--add-only", help="Add a repository without fetching it.", action="store_true",
                         dest="add_only", default=False)
repo_parser.set_defaults(func=repo.entry)

instance_parser = subparsers.add_parser('instance', help='Instance management', aliases=['ksp'])
instance_parser.add_argument("action", choices=instance.actions.keys())
instance_parser.add_argument("name", help="Name of the instance.", nargs="?")
instance_parser.add_argument("uri", help="Directory the instance is in.", nargs="?")
instance_parser.set_defaults(func=instance.entry)

search_parser = subparsers.add_parser('search', help='Search for mods.')
search_parser.add_argument("--name", help="Search for specific string in names.")
search_parser.add_argument("--desc", help="Search for specific string in descriptions.")
search_parser.add_argument("--kspver", help="Search for mods compatible with a specific version of KSP.")
search_parser.set_defaults(func=search.entry)

if __name__ == "__main__":
    args = parser.parse_args()
    args.func(args)
