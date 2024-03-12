from load_data import process_data
from calculate import get_slew_rates, attitude_knowledge_errors, calculate_angles_to_tracker, check_imaging_pass, valid_imaging_pass_lengths
import numpy as np
import json
import datetime

def number_good_passes(data_path):
    """
    Return number of good passes in file.
    """
    
    with open(data_path, "r") as file:
        data = json.load(file)

    good_passes = 0
    for imaging_pass in data["data"]:
        if imaging_pass["valid"]:
            good_passes += 1

    return good_passes

def all_imaging_times(file_path, placement):
    """
    Return list of all imaging times in file.
    """
    data = process_data(file_path)
    times = []
    for imaging_pass in data:
        pass_times = [instance[0] for instance in imaging_pass]
        times.extend(pass_times)
    return times

def slew_rates(data_path):
    """
    Return max slew rates of all imaging passes in file.
    """

    with open(data_path, "r") as file:
        data = json.load(file)

    max_slew_rates = []
    for imaging_pass in data["data"]:
        slew_rates = imaging_pass["slew_rates"]
        valid_slew_rates = []
        for index in imaging_pass["valid_indicies"]:
            valid_slew_rates.append(slew_rates[index - 1])
        if len(valid_slew_rates) > 0:
            max_slew_rates.append(np.max(valid_slew_rates))

    return max_slew_rates

def longest_valid_imaging_pass(data_path):
    """
    Return longest valid imaging pass in file.
    Find longest valid imaging pass by finding the pass with the most valid consecutive indicies.
    """

    with open(data_path, "r") as file:
        data = json.load(file)

    longest_pass = []
    longest_pass_index = 0
    for i in range(len(data["data"])):
        imaging_pass = data["data"][i]
        valid_indicies = imaging_pass["valid_indicies"]
        longest_consecutive_pass = []
        longest_consecutive_pass_index = 0
        consecutive_pass = []
        for j in range(len(valid_indicies)):
            if j == 0:
                consecutive_pass.append(valid_indicies[j])
            elif valid_indicies[j] == valid_indicies[j-1] + 1:
                consecutive_pass.append(valid_indicies[j])
            else:
                if len(consecutive_pass) > len(longest_consecutive_pass):
                    longest_consecutive_pass = consecutive_pass
                    longest_consecutive_pass_index = i
                consecutive_pass = [valid_indicies[j]]
        if len(consecutive_pass) > len(longest_consecutive_pass):
            longest_consecutive_pass = consecutive_pass
            longest_consecutive_pass_index = i
        if len(longest_consecutive_pass) > len(longest_pass):
            longest_pass = longest_consecutive_pass
            longest_pass_index = longest_consecutive_pass_index
    
    return len(longest_pass), longest_pass_index, longest_pass[0]

def num_valid_imaging_passes(data_path):
    """
    Return number of valid imaging passes in file.
    """

    with open(data_path, "r") as file:
        data = json.load(file)

    valid_passes = 0
    for imaging_pass in data["data"]:
        if len(imaging_pass["valid_indicies"]) > 0:
            valid_passes += 1

    return valid_passes
    

def get_pass_date_range(data_path, index, start_index, duration):
    """
    Get date range of imaging pass at index in file.
    """

    imaging_pass = get_imaging_pass(data_path, index)
    start_date = imaging_pass["start_date"]
    end_date = imaging_pass["end_date"]
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
    delta_t = 1 #TODO: Get delta_t from file
    start_date = start_date + datetime.timedelta(seconds=delta_t * start_index)
    end_date = start_date + datetime.timedelta(seconds=duration)

    return start_date, end_date

def get_imaging_pass(data_path, index):
    """
    Get imaging pass at index in file.
    """

    with open(data_path, "r") as file:
        data = json.load(file)

    return data["data"][index]

def attitude_knowledge_error(file_path, placement):
    """
    Return max attitude knowledge error of all imaging passes in file.
    """
    return []

def generate_analyzed_imaging_pass(imaging_pass, placement):
    slew_rates = get_slew_rates(imaging_pass)
    angles = calculate_angles_to_tracker(imaging_pass, placement)
    start_date = imaging_pass[0][0]
    end_date = imaging_pass[-1][0]
    valid_indicies = check_imaging_pass(imaging_pass, placement)

    return {
        "start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": end_date.strftime("%Y-%m-%d %H:%M:%S"),
        "slew_rates": slew_rates,
        "attitude_knowledge_error": attitude_knowledge_errors(slew_rates),
        "sun_angles": [instance[1] for instance in angles],
        "moon_angles": [instance[2] for instance in angles],
        "earth_angles": [instance[3] for instance in angles],
        "valid_indicies": valid_indicies,
        "pass_durations": valid_imaging_pass_lengths(imaging_pass, valid_indicies),
    }

def generate_analyzed_imaging_passes(stk_path, output_path, placement):
    data = process_data(stk_path)
    output = []
    for imaging_pass in data:
        analyzed_imaging_pass = generate_analyzed_imaging_pass(imaging_pass, placement)
        output.append(analyzed_imaging_pass)

    with open(output_path, 'w') as f:
        json.dump({
            "placement": placement,
            "data": output
        }, f)

def generate_speedometer_config(label, unit_text, values, yellow_zone, red_zone):
    """
    Generate a speedometer config file.
    """

    if len(values) == 0:
        return {}

    data_config = {}

    data_config["min_value"] = 0 # Speedometer makes more sense this way
    data_config["max_value"] = float(np.max(values))
    data_config["label"] = label
    data_config["unit_text"] = unit_text
    data_config["values"] = values

    if np.max(values) > yellow_zone[0]:
        if np.max(values) > yellow_zone[1]:
            data_config["yellow_zone"] = [yellow_zone[0], yellow_zone[1]]
        else:
            data_config["yellow_zone"] = [yellow_zone[0], float(np.max(values))]
    
    if np.max(values) > red_zone[0]:
        if np.max(values) > red_zone[1]:
            data_config["red_zone"] = [red_zone[0], red_zone[1]]
        else:
            data_config["red_zone"] = [red_zone[0], float(np.max(values))]

    return data_config


def generate_video_config_data(imaging_pass, output_path, start_index = 0, duration = 0):
    """
    Generate a video config file.
    """

    video_config = {}
    
    slew_rate_speedometer = generate_speedometer_config("Slew Rate", "DEG/SEC", imaging_pass["slew_rates"][start_index:start_index + duration], [0.4, 0.6], [0.6, 10])
    attitude_knowledge_speedometer = generate_speedometer_config("Error", "PX", imaging_pass["attitude_knowledge_error"][start_index:start_index + duration], [0.4, 0.6], [0.6, 10])
    sun_angles_speedometer = generate_speedometer_config("Sun Angle", "DEG", imaging_pass["sun_angles"][start_index:start_index + duration], [40, 50], [0, 40])
    earth_angles_speedometer = generate_speedometer_config("Earth Angle", "DEG", imaging_pass["earth_angles"][start_index:start_index + duration], [110, 120], [0, 110])
    moon_angles_speedometer = generate_speedometer_config("Moon Angle", "DEG", imaging_pass["moon_angles"][start_index:start_index + duration], [40, 50], [0, 40])
    
    video_config["speedometers"] = [slew_rate_speedometer, attitude_knowledge_speedometer, sun_angles_speedometer, earth_angles_speedometer, moon_angles_speedometer]
    video_config["speedometers"] = [speedometer for speedometer in video_config["speedometers"] if len(speedometer) > 0]

    with open("../VideoTools/config/" + output_path, "w") as file:
        json.dump(video_config, file)

def generate_video_config(path, imaging_pass_index, start_index = 0, duration = 0):
    with open(path, "r") as file:
        data = json.load(file)["data"]
        output_path = path.split("/")[-1].split(".")[0] + "-VIDEO.json"
        generate_video_config_data(data[imaging_pass_index], output_path, start_index, duration)

# generate_analyzed_imaging_passes("FINCH_StarTracker_Sample.txt", "X-AXIS-VALID.json", (1, 0, 0))
# generate_analyzed_imaging_passes("FINCH_StarTracker_Sample.txt", "Y-AXIS-VALID.json", (0, 1, 0))
# generate_analyzed_imaging_passes("FINCH_StarTracker_Sample.txt", "Z-AXIS-VALID.json", (0, 0, 1)) # Example of invalid placement

# generate_analyzed_imaging_passes("stk_data/FINCH_StarTracker_Oct18-17-00_Oct23-17-00.txt", "data/X-AXIS-OCT18-17-00-OCT23-17-00-VALID.json", (1, 0, 0))
# generate_analyzed_imaging_passes("stk_data/FINCH_StarTracker_Oct18-17-00_Oct23-17-00.txt", "data/Y-AXIS-OCT18-17-00-OCT23-17-00-VALID.json", (0, 1, 0))

# bestX = longest_valid_imaging_pass("data/X-AXIS-OCT18-17-00-OCT23-17-00-VALID.json")
# bestY = longest_valid_imaging_pass("data/Y-AXIS-OCT18-17-00-OCT23-17-00-VALID.json")
# datesX = get_pass_date_range("data/X-AXIS-OCT18-17-00-OCT23-17-00-VALID.json", bestX[1], bestX[2], bestX[0])
# datesY = get_pass_date_range("data/Y-AXIS-OCT18-17-00-OCT23-17-00-VALID.json", bestY[1], bestY[2], bestY[0])

# print(f"Best X-Axis Pass: {bestX[0]} seconds, {datesX[0]} to {datesX[1]}")
# print(f"Best Y-Axis Pass: {bestY[0]} seconds, {datesY[0]} to {datesY[1]}")

# generate_video_config("data/X-AXIS-OCT18-17-00-OCT23-17-00-VALID.json", bestX[1], bestX[2], bestX[0])
# generate_video_config("data/Y-AXIS-OCT18-17-00-OCT23-17-00-VALID.json", bestY[1], bestY[2], bestY[0])

# print(num_valid_imaging_passes("data/X-AXIS-OCT18-17-00-OCT23-17-00-VALID.json"))
# print(num_valid_imaging_passes("data/Y-AXIS-OCT18-17-00-OCT23-17-00-VALID.json"))

# sr = slew_rates("data/Y-AXIS-OCT18-17-00-OCT23-17-00-VALID.json")
# print(np.max(sr))
# print(np.mean(sr))