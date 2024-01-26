from load_data import process_data
from calculate import get_slew_rates, attitude_knowledge_errors, calculate_angles_to_tracker, check_imaging_pass

def number_good_passes(file_path, placement):
    """
    Return number of good passes in file.
    """
    return 0

def all_imaging_times(file_path, placement):
    """
    Return list of all imaging times in file.
    """
    return []

def slew_rates(file_path, placement):
    """
    Return max slew rate of all imaging passes in file.
    """
    return []

def attitude_knowledge_error(file_path, placement):
    """
    Return max attitude knowledge error of all imaging passes in file.
    """
    return []

def generate_analyzed_imaging_pass(imaging_pass, placement):
    """
    Generate a JSON data file.

    Example JSON:
    {
        "start_date": "",
        "end_date": "",
        "slew_rates": [],
        "attitude_knowledge_error": [],
        "sun_angles": [],
        "earth_angles": [],
        "moon_angles": [],
        "valid": True
    }
    """

    slew_rates = get_slew_rates(imaging_pass)
    angles = calculate_angles_to_tracker(imaging_pass, placement)

    return {
        "start_date": imaging_pass[0][0],
        "end_date": imaging_pass[-1][0],
        "slew_rates": slew_rates,
        "attitude_knowledge_error": attitude_knowledge_errors(slew_rates),
        "sun_angles": [instance[2] for instance in angles],
        "earth_angles": [instance[4] for instance in angles],
        "moon_angles": [instance[3] for instance in angles],
        "valid": check_imaging_pass(imaging_pass, placement)
    }

def generate_analyzed_imaging_passes(stk_path, output_path, placement):
    data = process_data(stk_path)
    output = []
    for imaging_pass in data:
        output.append(generate_analyzed_imaging_pass(imaging_pass, placement))
    
    with open(output_path, 'w') as f:
        f.write(output)

def generate_video_config(imaging_pass_path, output_path):
    """
    Generate a video config file.
    """
    pass