from libckan.cache import CKANVersion


def test_version():
    assert CKANVersion("1.1") == CKANVersion("0:1.1")
    assert CKANVersion("1.1") == CKANVersion("0:1.1")
    assert CKANVersion("1.2") > CKANVersion("0:1.1")
    assert CKANVersion("0.2.0") > CKANVersion("0.1.9")
    assert CKANVersion("v0.2.0") > CKANVersion("v0.1.9")
    assert CKANVersion("v0.2.1") > CKANVersion("v0.2.0_pre")
    assert CKANVersion("v0.2.1a") < CKANVersion("v0.2.1b")
    assert CKANVersion("alpha") < CKANVersion("beta")
    assert CKANVersion("v6a1") < CKANVersion("v6a12")
    assert CKANVersion("1.1.1") > CKANVersion("1.1.0.0")
    assert CKANVersion("1.01") == CKANVersion("1.1")
    assert CKANVersion("1.0") < CKANVersion("1.0.repackaged") < CKANVersion("1.1.1")
    assert CKANVersion("v0.15.3.1") < CKANVersion("3:0.15.6.3")
    assert CKANVersion("v0.15.3.1") < CKANVersion("1:v0.15.3.1")
    assert CKANVersion("1") < CKANVersion("1:1")
