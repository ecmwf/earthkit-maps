import earthkit.maps


def test_version() -> None:
    assert earthkit.maps.__version__ != "999"
