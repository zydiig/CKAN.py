# Inspired by https://github.com/KSP-CKAN/CKAN/blob/master/Core/Types/Version.cs#L76
def _str_comp(a, b):
    ar = ""
    br = ""
    for idx, chr in enumerate(a):
        if chr.isdigit():
            ar = a[idx:]
            a = a[:idx - 1]
            break
    for idx, chr in enumerate(b):
        if chr.isdigit():
            br = b[idx:]
            b = b[:idx - 1]
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


# This too.
def _num_comp(a, b):
    ar = ""
    br = ""
    for idx, chr in enumerate(a):
        if not chr.isdigit():
            ar = a[idx:]
            a = a[:idx - 1]
            break
    for idx, chr in enumerate(b):
        if not chr.isdigit():
            br = b[idx:]
            b = b[:idx - 1]
            break
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
