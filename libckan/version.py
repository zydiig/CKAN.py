import re
from functools import total_ordering


def _str_comp(a: str, b: str):
    """
    Inspired by https://github.com/KSP-CKAN/CKAN/blob/master/Core/Types/Version.cs#L76
    A delicate process
    """
    ar = ""
    br = ""
    for idx, chr in enumerate(a):
        if chr.isdigit():
            ar = a[idx:]
            a = a[:idx]
            break
    for idx, chr in enumerate(b):
        if chr.isdigit():
            br = b[idx:]
            b = b[:idx]
            break
    ret = 0
    if len(a) > 0 and len(b) > 0:
        if a[0] != "." and b[0] == ".":
            ret = -1
        elif a[0] == "." and b[0] != ".":
            ret = 1
        elif a[0] == "." and b[0] == ".":
            if len(a) == 1 and len(b) > 1:
                ret = 1
            elif len(a) > 1 and len(b) == 1:
                ret = -1
        else:
            if a < b:
                ret = -1
            elif a == b:
                ret = 0
            elif a > b:
                ret = 1
    else:
        if a < b:
            ret = -1
        elif a == b:
            ret = 0
        elif a > b:
            ret = 1
    return ret, ar, br


def _num_comp(a, b):
    """This too."""
    ar = ""
    br = ""
    for idx, chr in enumerate(a):
        if not chr.isdigit():
            ar = a[idx:]
            a = a[:idx]
            break
    for idx, chr in enumerate(b):
        if not chr.isdigit():
            br = b[idx:]
            b = b[:idx]
            break
    ret = 0
    ai = 0 if len(a) == 0 else int(a)
    bi = 0 if len(b) == 0 else int(b)
    if ai < bi:
        ret = -1
    elif ai == bi:
        ret = 0
    elif ai > bi:
        ret = 1
    return ret, ar, br


def version_comp(a, b):
    while len(a) != 0 and len(b) != 0:
        ret, a, b = _str_comp(a, b)
        if ret != 0:
            return ret
        ret, a, b = _num_comp(a, b)
        if ret != 0:
            return ret
    if len(a) == 0 and len(b) == 0:
        return 0
    else:
        return -1 if len(a) == 0 else 1


@total_ordering
class KSPVersion:
    def __init__(self, *kargs):
        if len(kargs) == 1:
            self.version_string = kargs[0]
            self.major, self.minor, self.patch = kargs[0].split(".")
        elif len(kargs) == 3:
            self.version_string = ".".join(kargs)
            self.major, self.minor, self.patch = kargs

    def __eq__(self, other):
        if version_comp(self.version_string, other.version_string) == 0:
            return True
        return False

    def __gt__(self, other):
        if version_comp(self.version_string, other.version_string) == 1:
            return True
        return False

    def __lt__(self, other):
        if version_comp(self.version_string, other.version_string) == -1:
            return True
        return False


class KSPVersionConstraint:
    def __init__(self, *kargs):
        if len(kargs) == 0:
            return
        elif len(kargs) == 1:
            self.min = kargs[0]
            self.max = kargs[0]
        elif len(kargs) == 2:
            self.min = kargs[0]
            self.max = kargs[1]

    def check(self, version: KSPVersion):
        if self.min and self.max:
            return self.min <= version <= self.max
        elif self.min and not self.max:
            return version >= self.min
        elif self.max and not self.min:
            return version <= self.max
        else:
            return True


class CKANVersion:
    def __init__(self, version_string):
        self.version_string = version_string
        match = re.match(r"((\d+):)?(.+)", version_string)
        if not match.group(2):
            self.epoch = 0
        else:
            self.epoch = int(match.group(2))
        self.version = match.group(3)

    def __lt__(self, other):
        if self.epoch < other.epoch:
            return True
        elif self.epoch == other.epoch and version_comp(self.version, other.version) == -1:
            return True
        else:
            return False

    def __gt__(self, other):
        if self.epoch > other.epoch:
            return True
        elif self.epoch == other.epoch and version_comp(self.version, other.version) == 1:
            return True
        else:
            return False

    def __eq__(self, other):
        if self.epoch == other.epoch and version_comp(self.version, other.version) == 0:
            return True
        return False

    def __ge__(self, other):
        return self == other or self > other

    def __le__(self, other):
        return self == other or self < other

    def __str__(self):
        return self.version_string

    def __repr__(self):
        return self.version_string


class CKANAtom:
    def __init__(self, *kargs):
        if len(kargs) == 1:  # from a atom string
            m = re.fullmatch(r"((?:>=)|(?:<=)|(?:=)|(?:>)|(?:<))?(.*?)(?:-(.*))?", kargs[0])
            print(m.groups())
            self.op = m.group(1) or None
            self.identifier = m.group(2)
            self.version = CKANVersion(m.group(3)) if m.group(3) else None
        elif len(kargs) == 3:  # from the parts
            op = kargs[0]
            if not op in [">", "<", "=", ">=", "<="]:
                raise Exception("Illegal operator")
            self.op = op
            self.identifier = kargs[1]
            self.version = CKANVersion(kargs[2])

    def to_expr(self):
        if self.op or self.version:
            return 'CKANVersion(b["version"]) {op} self.version'.format(op=self.op)
        else:
            return "True"

    def find_build(self, cache):
        results = cache.search(lambda x: x["identifier"] == self.identifier)
        if len(results) > 1:
            raise Exception("Too many matches")
        elif len(results) == 0:
            raise Exception("No match")
        return results[0].get_build(lambda b: eval(self.to_expr()))
