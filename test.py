from libckan.cache import CKANVersion

vs = ["1:1.1", "1:1.2", "2:1.1.5"]

print(max(vs, key=CKANVersion))
