
# Compare this vector to sun, earth, and moon vectors
# Check if angle violates constraints

def calculate_angles(imaging_pass, placement):
    """
    Takes [[time, sun x, sun y, sun z, ...], [time, sun x, sun y, sun z, ...]]
    Return [[time, sun angle, moon angle, ...], ..]
    """
    return []

def violates_sun_constraint(angle):
    """
    Return True if angle violates sun constraint. (< 40 deg)
    """
    return False

def violates_earth_constraint(angle):
    """
    Return True if angle violates earth constraint.
    Check 40 deg cone intersection with 100 km atmosphere. (~110 deg)
    Source: https://www.researching.cn/articles/OJc35aead846202911
    """
    return False

def violates_moon_constraint(angle):
    """
    Return True if angle violates moon constraint. (< 40 deg)
    """
    return False

def check_imaging_pass(imaging_pass, placement = (1, 0, 0)):
    """
    Return True if imaging pass is valid.
    """
    return False

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