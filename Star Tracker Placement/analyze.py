import numpy as np
import json
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

def generate_analyzed_imaging_pass(file_path, placement):
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
    }
    """
    pass

def generate_video_config(imaging_pass_path, output_path):
    """
    Generate a video config file.
    
    """
    with open(imaging_pass_path, "r") as file:
        imaging_pass_data = json.load(file)
    
    data_config = {}

    slew_rates_data = {}
    
    slew_rates_data["min_value"] =  np.min(imaging_pass_data["slew_rates"])
    slew_rates_data["max_value"] =  np.max(imaging_pass_data["slew_rates"])
    slew_rates_data["unit_text"] =  "DEG/SEC"
    slew_rates_data["label"] =  "SLEW RATE"
    slew_rates_data["values"] =  [0, 100, 0, 100, 0, 100, 0, 100, 0, 100, 100]
    slew_rates_data["yellow_zone"] =  [0.4, 0.6]
    if slew_rates_data["max_value"]>0.6:
        slew_rates_data["red_zone"] =  [0.6, slew_rates_data["max_value"]]

    attitude_knowledge_error_data = {}
    
    attitude_knowledge_error_data["min_value"] =  np.min(imaging_pass_data["attitude_knowledge_error"])
    attitude_knowledge_error_data["max_value"] =  np.max(imaging_pass_data["attitude_knowledge_error"])
    attitude_knowledge_error_data["unit_text"] =  "PX"
    attitude_knowledge_error_data["label"] =  "ERROR"
    attitude_knowledge_error_data["values"] =  [0, 50, 60, 10, 50, 60, 80, 100, 0, 100, 100]
    # attitude_knowledge_error_data["yellow_zone"] =  [0.4, 0.6]
    # attitude_knowledge_error_data["red_zone"] =  [0.6, slew_rates_data.max_value]


    sun_angles_data = {}

    sun_angles_data["min_value"] =  np.min(imaging_pass_data["sun_angles"])
    sun_angles_data["max_value"] =  np.max(imaging_pass_data["sun_angles"])
    sun_angles_data["unit_text"] =  "DEGREES"
    sun_angles_data["label"] =  "SUNANGLE"
    sun_angles_data["values"] =  [0, 50, 60, 10, 50, 60, 80, 100, 0, 100, 100]
    sun_angles_data["yellow_zone"] =  [70, 75]
    sun_angles_data["red_zone"] =  [sun_angles_data["min_value"], 65]

    earth_angles_data = {}

    earth_angles_data["min_value"] =  np.min(imaging_pass_data["earth_angles"])
    earth_angles_data["max_value"] =  np.max(imaging_pass_data["earth_angles"])
    earth_angles_data["unit_text"] =  "DEGREES"
    earth_angles_data["label"] =  "EARTHANGLE"
    earth_angles_data["values"] =  [0, 50, 60, 10, 50, 60, 80, 100, 0, 100, 100]
    earth_angles_data["yellow_zone"] =  [70, 75]
    earth_angles_data["red_zone"] =  [earth_angles_data["min_value"], 65]
    
    moon_angles_data = {}

    moon_angles_data["min_value"] =  np.min(imaging_pass_data["moon_angles"])
    moon_angles_data["max_value"] =  np.max(imaging_pass_data["moon_angles"])
    moon_angles_data["unit_text"] =  "DEGREES"
    moon_angles_data["label"] =  "MOONANGLE"
    moon_angles_data["values"] =  [0, 50, 60, 10, 50, 60, 80, 100, 0, 100, 100]
    moon_angles_data["yellow_zone"] =  [70, 75]
    moon_angles_data["red_zone"] =  [moon_angles_data["min_value"], 65]

    data_config["speedometers"] = [slew_rates_data,attitude_knowledge_error_data,sun_angles_data,earth_angles_data,moon_angles_data]

    with open(output_path, "w") as file:
        json.dump(data_config,file)

    pass

generate_video_config("example_imaging_pass.json","data.json")