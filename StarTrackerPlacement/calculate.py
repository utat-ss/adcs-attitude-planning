import math

def magnitude(vector):
    return math.sqrt(sum([x**2 for x in vector]))

def normalize(vector):
    return [component/magnitude(vector) for component in vector]

def radians_to_degrees(radians):
    return radians * 180.0 / math.pi

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

# Compare this vector to sun, earth, and moon vectors
# Check if angle violates constraints
def vecs_to_angle(vector1, vector2):
    """
    Takes two vectors as [x1, y1, z1] and [x2, y2, z2]
    Returns the angle between the vectors in degrees as float
    """

    normed1 = normalize(vector1)
    normed2 = normalize(vector2)

    dotted = sum([comp1 * comp2 for comp1, comp2 in zip(normed1, normed2)])
    
    dotted = clamp(dotted, -1, 1)

    angle = math.acos(dotted)

    return radians_to_degrees(angle)

def get_angle_safe(vector1, vector2):
    try:
        return vecs_to_angle(vector1, vector2)
    except:
        return 180
    
def is_in_eclipse(imaging_pass_instance):
    """
    Takes [[time, sun x, sun y, sun z, ...], [time, sun x, sun y, sun z, ...]]
    Return True if imaging pass is in eclipse.
    """
    sunlightvec = imaging_pass_instance[4:7]
    return sunlightvec[0] == 0 and sunlightvec[1] == 0 and sunlightvec[2] == 0

def calculate_angles_to_tracker(imaging_pass, placement):
    """
    Takes [[time, sun x, sun y, sun z, ...], [time, sun x, sun y, sun z, ...]] and [placementx, placementy, placementz]
    Return [[time, sun angle, moon angle, earth angle], ..]
    """
    angles = []
    for instance in imaging_pass:
        sunvec = instance[1:4]
        moonvec = instance[7:10]
        earthvec = instance[10:13]

        angle_instance = [instance[0], get_angle_safe(sunvec,placement), get_angle_safe(moonvec,placement), get_angle_safe(earthvec,placement)]
        angles.append(angle_instance)
    
    return angles


def violates_sun_constraint(angle):
    """
    Return True if angle violates sun constraint. (< 40 deg)
    """
    return angle < 40

EARTH_RADIUS = 6371.0 #km
def violates_earth_constraint(angle, dist_to_earth=500):
    """
    Return True if angle violates earth constraint.
    Check 40 deg cone intersection with 100 km atmosphere. (~110 deg)
    Source: https://www.researching.cn/articles/OJc35aead846202911
    """
    atm_width = 100.0 #km
    sin_angle = (EARTH_RADIUS + atm_width)/(EARTH_RADIUS + dist_to_earth)
    sin_angle = clamp(sin_angle, -1, 1)
    earthlight_cone_angle = math.asin(sin_angle)  #δa=arcsin[(Er+d)/Es], from paper
    earthlight_cone_angle = radians_to_degrees(earthlight_cone_angle)
    return angle < earthlight_cone_angle + 40

def violates_moon_constraint(angle):
    """
    Return True if angle violates moon constraint. (< 40 deg)
    """
    return angle < 40

def is_instance_valid(angle_instance, imaging_pass_instance):
    return not violates_sun_constraint(angle_instance[1]) and not violates_moon_constraint(angle_instance[2]) and not violates_earth_constraint(angle_instance[3]) and not is_in_eclipse(imaging_pass_instance)

def check_imaging_pass(imaging_pass, placement = (1, 0, 0)):
    """
    Return indicies of imaging pass that are valid.
    """

    angles = calculate_angles_to_tracker(imaging_pass, placement)
    indices = []
    for i in range(len(angles)):
        angles_instance = angles[i]
        if is_instance_valid(angles_instance, imaging_pass[i]):
            indices.append(i)

    return indices

def valid_imaging_pass_lengths(imaging_pass, indicies):
    """
    Return list of valid imaging pass lengths by checking consecutive indicies.
    Also include start index, e.g. [(0, 100), (145, 200)]
    """
    
    lengths = []
    if len(indicies) == 0:
        return lengths
    start = indicies[0]
    end = indicies[0]
    for i in range(1, len(indicies)):
        if indicies[i] == indicies[i-1] + 1:
            end = indicies[i]
        else:
            lengths.append((start, end - start + 1))
            start = indicies[i]
            end = indicies[i]
    lengths.append((start, end - start + 1))

    delta_t = imaging_pass[1][0] - imaging_pass[0][0]
    delta_t = delta_t.total_seconds()
    lengths = [(length[0] * delta_t, length[1]) for length in lengths]

    return lengths


def get_slew_rates(imaging_pass):
    """
    Takes [[time (datetime), sun x, sun y, sun z, ...], [time (datetime), sun x, sun y, sun z, ...]]

    Return list of slew rate over time for imaging pass.
    ((angle with earth)(t + 1) - (angle with earth)(t)) / delta_t
    """
    
    slew_rates = []
    for i in range(len(imaging_pass) - 1):
        delta_angle = vecs_to_angle(imaging_pass[i][10:13], imaging_pass[i+1][10:13])
        delta_t = imaging_pass[i+1][0] - imaging_pass[i][0]
        delta_t = delta_t.total_seconds()
        slew_rate = delta_angle/delta_t
        slew_rates.append(slew_rate)

    return slew_rates

def max_slew_rate(imaging_pass):
    """
    Return max slew rate over imaging pass.
    """
    return 0

def attitude_knowledge_errors(slew_rates):
    """
    Return attitude knowledge error over imaging pass.
    """
    return []