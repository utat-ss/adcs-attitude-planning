from classes.orbit_path import OrbitPath
from tools.file_processing import import_STK_data

if __name__ == "__main__":
    list_data = import_STK_data(r'AttitudePipeline\data\FINCH_StarTracker_Sample.txt')
    full_path = OrbitPath.construct_STK(list_data)
    full_path.apply_placement((1,0,0))
    full_path.apply_checks()

    full_path.fragment_passes()

    longest_pass, interval = full_path.get_longest_imaging_pass()

    print(interval)