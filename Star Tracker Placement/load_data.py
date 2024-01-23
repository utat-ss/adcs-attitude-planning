def process_data(file_path):
    """
    Return triple array of relevant info for each imaging pass.

    E.g. [[[time, sun x, sun y, sun z, ...], [time, sun x, sun y, sun z, ...]], ...]
    """

    with open(file_path) as f:
        lines = f.readlines()

    target_data = []
    coords = []
    block_count = 0

    for line in lines:
        if line[0] == '-':
            block_count += 1
            continue

        if block_count == 1 and line != '\n':
            target_data.append(line)
        elif block_count == 2:
            coords.append(line)

    print(coords)
    return target_data, coords

process_data('FINCH_StarTracker_Sample.txt')