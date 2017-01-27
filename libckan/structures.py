import re
from pathlib import Path


class Filter:
    NAME = 1
    REGEXP = 2

    def __init__(self, type, pattern):
        self.type = type
        self.pattern = pattern

    def check(self, path: Path):
        if self.type == Filter.NAME:
            return path.name != self.pattern
        elif self.type == Filter.REGEXP:
            return not re.fullmatch(self.pattern, str(path))
