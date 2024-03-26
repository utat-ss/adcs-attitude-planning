from classes.orbit_path import OrbitPath
from tools.file_processing import import_STK_data

if __name__ == "__main__":
    list_data = import_STK_data('AttitudePipeline\data\FINCH_StarTracker_Sample.txt')
    print(list_data[0][0])
    full_path = OrbitPath.construct_STK(list_data)
    print([full_path.img_passes[0].instances])
    print()
    