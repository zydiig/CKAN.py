import argparse
import logging
import sys
from pathlib import Path

import install
import instance
import repo
import search
from config import get_current_instance, Instance, Settings

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument("--kspdir", help="KSP directory to operate in", type=str, nargs="?")
parser.add_argument("--instance", help="Name of KSP instance to operate on", type=str, nargs="?", dest="instance_name")
modules = {"instance": instance, "repo": repo}
subparsers = parser.add_subparsers(help="Modules to invoke")

repo_parser = subparsers.add_parser('repo', help='Repository management')
repo_parser.add_argument("action", choices=repo.actions.keys())
repo_parser.add_argument("name", help="Name of the repository", nargs="?")
repo_parser.add_argument("uri", help="URI of the repository", nargs="?")
repo_parser.add_argument("--add-only", help="Add a repository without fetching it", action="store_true",
                         dest="add_only", default=False)
repo_parser.set_defaults(func=repo.entry)

instance_parser = subparsers.add_parser('instance', help='Instance management', aliases=['ksp'])
instance_parser.add_argument("action", choices=instance.actions.keys())
instance_parser.add_argument("name", help="Name of the instance", nargs="?")
instance_parser.add_argument("uri", help="Directory the instance is in", nargs="?")
instance_parser.set_defaults(func=instance.entry)

search_parser = subparsers.add_parser('search', help='Search for mods')
search_parser.add_argument("--name", help="Search for specific string in names")
search_parser.add_argument("--desc", help="Search for specific string in descriptions")
search_parser.add_argument("--kspver", help="Search for mods compatible with a specific version of KSP")
search_parser.set_defaults(func=search.entry)

install_parser = subparsers.add_parser('install', help='Install mods')
install_parser.add_argument("id", help="Identifiers of mods to install.", nargs="+")
install_parser.add_argument("--dry-run", help="Simulate installation process.", action="store_true", dest="dry_run",
                            default=False)
install_parser.set_defaults(func=install.install)

remove_parser = subparsers.add_parser('install', help='Remove mods')
remove_parser.add_argument("id", help="Identifiers of mods to remove.", nargs="+")
remove_parser.add_argument("--dry-run", help="Simulate removal process.", action="store_true", dest="dry_run",
                           default=False)
remove_parser.set_defaults(func=install.remove)

if __name__ == "__main__":
    args = parser.parse_args()
    if not (Path("~") / ".ckanpy.cfg").expanduser().exists():
        print("This is the first time you've run CKAN.py.")
        print("Please create a new KSP instance.")
        path = input("Path to KSP directory: ")
        if Path(path).exists():
            Settings.create(path)
        else:
            logging.error("Path is not a directory.Exiting.")
            sys.exit(1)
    s = Settings()
    if args.kspdir:
        args.instance = Instance(args.kspdir)
    elif args.instance_name:
        args.instance = s.get_instance_by_name(args.instance_name)
    else:
        args.instance = get_current_instance()
    logging.info(args)
    args.func(args)
