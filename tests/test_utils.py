from magpye import utils


def test_recursive_dict_update():
    dict_1 = {"nested": {"a": 1, "b": 2}, "c": 3, "d": 4}
    dict_2 = {"nested": {"a": 10, "c": 3}, "d": 5, "e": 6}

    expected = {"nested": {"a": 10, "b": 2, "c": 3}, "c": 3, "d": 5, "e": 6}

    assert utils.recursive_dict_update(dict_1, dict_2) == expected
