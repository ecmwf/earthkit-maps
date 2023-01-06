from magpye import _data


def test_load():
    domains = _data.load("domains")
    assert isinstance(domains, dict) and "domains" in domains
