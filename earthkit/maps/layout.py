def auto_rows_cols(num_subplots, max_cols=8):
    presets = {
        1: (1, 1),
        2: (1, 2),
        3: (1, 3),
        4: (1, 4),
        5: (2, 3),
        6: (2, 3),
        7: (2, 4),
        8: (2, 4),
        9: (2, 5),
        10: (2, 5),
        11: (3, 4),
        12: (3, 4),
        13: (3, 5),
        14: (3, 5),
        15: (3, 5),
        16: (3, 6),
        17: (3, 6),
        18: (3, 6),
        19: (4, 5),
        20: (4, 5),
    }

    if num_subplots in presets:
        rows, cols = presets[num_subplots]
    else:
        cols = max_cols
        rows = num_subplots // max_cols + 1

    return rows, cols
