from datetime import datetime

def import_STK_data(file_path: str) -> list[list[list]]:
    """ Return triple array of relevant info from standard format STK file.
        Output is of form: [[[date, sun x, sun y, sun z, ...], [date, sun x, sun y, sun z, ...]], ...]
        With each innermost list of form [date, Sun x, y, z, Sunlight x, y, z, Moon x, y, z, Earth x, y, z] all values in km, date of type datetime
        """
    
    def parse_data(file_path):
        with open(file_path) as f:
            lines = f.readlines()

        target_data = []
        coords = []
        block_count = 0
        reading = False

        for line in lines:
            if line[0] == '-':
                reading = True
                block_count += 1
                continue

            if line == '\n':
                reading = False
                continue

            if block_count == 1 and reading:
                line = line.strip()
                line = line.split('    ')
                line = [x.strip() for x in line if x != '']
                line[0] = datetime.strptime(line[0], "%d %b %Y %H:%M:%S.%f") # type: ignore
                line[1] = datetime.strptime(line[1], "%d %b %Y %H:%M:%S.%f") # type: ignore
                target_data.append(line)
            elif block_count == 2 and reading:
                line = line.strip()
                line = line.split('    ')
                line = [x.strip() for x in line if x != '']
                line[0] = datetime.strptime(line[0], "%d %b %Y %H:%M:%S.%f") # type: ignore
                for i in range(1, len(line)):
                    line[i] = float(line[i]) # type: ignore
                coords.append(line)

        return target_data, coords

    target_data, coords = parse_data(file_path)
    tracking_periods = [x for x in target_data if x[3] == 'Target']

    res = []
    current_coords_index = 0
    for period in tracking_periods:
        start = period[0]
        end = period[1]
        imaging_pass = []
        while current_coords_index < len(coords) and coords[current_coords_index][0] <= end:
            if coords[current_coords_index][0] >= start:
                imaging_pass.append(coords[current_coords_index])
            current_coords_index += 1
        if len(imaging_pass) > 0 and current_coords_index != len(coords) - 1:
            res.append(imaging_pass)

    return res