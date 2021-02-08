import json


def pad_grid(list_: list, shell_size: int) -> None:
    """Add padding to list_ on all sides of size shell_size."""
    row_padding = [0]*shell_size
    for row in list_:
        row[:0] = row_padding
        row.extend(row_padding)

    list_[:0] = [[0]*len(list_[0]) for _ in range(shell_size)]
    list_.extend([[0]*len(list_[0]) for _ in range(shell_size)])


def load_grids_from_file(file):
    grids_data = json.loads(file.read_bytes())
    for grid in grids_data["templates"].values():
        grid[:] = grid[::-1]
    return grids_data


def load_grid_from_file(file):
    grid = json.loads(file.read_bytes())
    return grid[::-1]
