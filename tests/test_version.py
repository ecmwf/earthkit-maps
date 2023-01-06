import magpye


def test_version() -> None:
    assert magpye.__version__ != "999"
