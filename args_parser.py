def parse_args(argv: list[str]):
    params_dict = {}
    for arg in argv:
        row = [i.strip() for i in arg.split('=', 1)]
        if len(row) > 1:
            if row[1].startswith('\'') and row[1].endswith('\'') or row[1].startswith('"') and row[1].endswith('"'):
                row[1] = row[1][1:-1]
            params_dict[row[0]] = row[1]
    return params_dict
