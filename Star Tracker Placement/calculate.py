import math

# Compare this vector to sun, earth, and moon vectors
# Check if angle violates constraints
def vecs_to_angle(vector1, vector2):
    """
    Takes two vectors as [x1, y1. z1] and [x2, y2, z2]
    Returns the angle between the vectors in degrees as float
    """
    # normalize: 
    normed1 = [component/(sum([x**2 for x in vector1])) for component in vector1]
    normed2 = [component/(sum([x**2 for x in vector2])) for component in vector2]

    dotted = sum([comp1 * comp2 for comp1, comp2 in zip(normed1, normed2)])

    angle = math.acos(dotted)

    return angle * 180.0 / math.pi

def calculate_angles_to_tracker(imaging_pass, placement):
    """
    Takes [[time, sun x, sun y, sun z, ...], [time, sun x, sun y, sun z, ...]] and [placementx, placementy, placementz]
    Return [[time, sun angle, moon angle, ...], ..]
    """
    for instance in imaging_pass:
        sunvec = instance[1:4]
        sunlightvec = instance[4:7]
        moonvec = instance[7:10]
        earthvec = instance[10:13]

        angle_instance = [instance[0], vecs_to_angle(sunvec,placement), vecs_to_angle(sunlightvec,placement), vecs_to_angle(moonvec,placement), vecs_to_angle(earthvec,placement)]
    return angles


def violates_sun_constraint(angle):
    """
    Return True if angle violates sun constraint. (< 40 deg)
    """
    return angle < 40

def violates_earth_constraint(angle, dist_to_earth):
    """
    Return True if angle violates earth constraint.
    Check 40 deg cone intersection with 100 km atmosphere. (~110 deg)
    Source: https://www.researching.cn/articles/OJc35aead846202911
    """
    earth_radius = 6371.0 #km
    atm_width = 100.0 #km
    earthlight_cone_angle = math.arcsin((earth_radius + atm_width)/dist_to_earth)  #δa=arcsin[(Er+d)/Es], from paper
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
        if violates_sun_constraint(instance[2]) or violates_moon_constraint(instance[3]) or violates_earth_constraint(instance[4]):
            return False

    return True


def get_slew_rates(imaging_pass):
    """
    Return list of slew rate over time for imaging pass.
    ((angle with earth)(t + 1) - (angle with earth)(t)) / delta_t
    """
    return []

def max_slew_rate(imaging_pass):
    """
    Return max slew rate over imaging pass.
    """
    return 0