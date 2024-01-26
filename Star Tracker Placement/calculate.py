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
    
def is_in_eclipse(imaging_pass):
    """
    Takes [[time, sun x, sun y, sun z, ...], [time, sun x, sun y, sun z, ...]]
    Return True if imaging pass is in eclipse.
    """
    for instance in imaging_pass:
        sunlightvec = instance[4:7]
        if sunlightvec[0] == 0 and sunlightvec[1] == 0 and sunlightvec[2] == 0:
            return True
    return False

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


def check_imaging_pass(imaging_pass, placement = (1, 0, 0)):
    """
    Return True if imaging pass is valid.
    """

    angles = calculate_angles_to_tracker(imaging_pass, placement)
    for instance in angles:
        if violates_sun_constraint(instance[1]) or violates_moon_constraint(instance[2]) or violates_earth_constraint(instance[3]):
            return False

    return True


def get_slew_rates(imaging_pass):
    """
    Takes [[time (datetime), sun x, sun y, sun z, ...], [time (datetime), sun x, sun y, sun z, ...]]

    Return list of slew rate over time for imaging pass.
    ((angle with earth)(t + 1) - (angle with earth)(t)) / delta_t
    """
    
    slew_rates = []
    for i in range(len(imaging_pass) - 1):
        angle1 = vecs_to_angle(imaging_pass[i][10:13], (0, 0, 1))
        angle2 = vecs_to_angle(imaging_pass[i+1][10:13], (0, 0, 1))
        delta_t_datetime = imaging_pass[i+1][0] - imaging_pass[i][0]
        delta_t = delta_t_datetime.total_seconds()
        slew_rate = (angle2 - angle1)/delta_t
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