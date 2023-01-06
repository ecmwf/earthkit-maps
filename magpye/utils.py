import collections


def recursive_dict_update(original_dict, update_dict):
    """
    Recursively update a dictionary with keys and values from another dictionary.

    Parameters
    ----------
    original_dict : dict
        The original dictionary to be updated (in place).
    update_dict : dict
        The dictionary containing keys to be updated in the original dictionary.
    """
    for k, v in update_dict.items():
        if isinstance(v, collections.abc.Mapping):
            original_dict[k] = recursive_dict_update(original_dict.get(k, {}), v)
        else:
            original_dict[k] = v
    return original_dict
