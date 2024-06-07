def parse_args(argv: list[str]):
    params_dict = {}
    for arg in argv:
        row = arg.split('=', 1)
        if len(row) > 1:
            params_dict[row[0]] = row[1]
    return params_dict
