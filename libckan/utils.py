from hashlib import sha1, sha256
from pathlib import Path
from urllib.parse import urlparse


def get_filename(url):
    return Path(urlparse(url)[2]).name


def get_sha1(data):
    h = sha1()
    h.update(data)
    return h.hexdigest().upper()


def get_sha256(data):
    h = sha256()
    h.update(data)
    return h.hexdigest().upper()
