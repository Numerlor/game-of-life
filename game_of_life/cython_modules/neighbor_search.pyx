cpdef (int, int, int, int, int, int, int, int, int) get_neighbor_indices(int x, int y, int x_start, int y_start, int col_count, int row_count):
    x = x - x_start
    y = y - y_start
    return (
        ((y - 1) % row_count) * col_count + (x - 1) % col_count,
        ((y - 1) % row_count) * col_count + x,
        ((y - 1) % row_count) * col_count +(x + 1) % col_count,

        y * col_count + (x - 1) % col_count,
        y * col_count + x,
        y * col_count + (x + 1) % col_count,

        ((y + 1) % row_count) * col_count +(x - 1) % col_count,
        ((y + 1) % row_count) * col_count + x,
        ((y + 1) % row_count) * col_count +(x + 1) % col_count,


    )