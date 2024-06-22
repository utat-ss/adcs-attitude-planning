import math
import numpy as np
import geopy.distance
from .convert import ecef2lla, quat2euler

def apply_quat(q, v):
    '''
    Applies a quaternion rotation to a vector.
    '''
    x, y, z = v
    a, b, c, d = q

    return [
        (a**2 + b**2 - c**2 - d**2) * x + 2 * (b*c - a*d) * y + 2 * (a*c + b*d) * z,
        2 * (b*c + a*d) * x + (a**2 - b**2 + c**2 - d**2) * y + 2 * (c*d - a*b) * z,
        2 * (b*d - a*c) * x + 2 * (a*b + c*d) * y + (a**2 - b**2 - c**2 + d**2) * z
    ]

def normalize(v):
    '''
    Normalizes a vector.
    '''
    norm = math.sqrt(sum([x**2 for x in v]))
    return [x / norm for x in v]

def mag(v):
    return math.sqrt(sum([x**2 for x in v]))

def ang_between_vecs(v1: np.ndarray, v2:np.ndarray) -> float:
    """Takes two vectors v1, v2 as numpy arrays and returns the angle between them in degrees"""
    normv1, normv2 = np.linalg.norm(v1), np.linalg.norm(v2)
    ang = np.arccos(np.dot(v1,v2)/ (normv1 * normv2))
    return np.rad2deg(ang)

def quaternion_multiply(quaternion1, quaternion2):
    w1, x1, y1, z1 = quaternion1
    w2, x2, y2, z2 = quaternion2
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
    return [w, x, y, z]

def dist_between_lat_lon(lat1, lon1, lat2, lon2):
    return geopy.distance.distance((lat1, lon1), (lat2, lon2)).m

def georef(v, q):
    """
    Apply rotation and find latitude and longitude of intersection with Earth.
    """
    d = apply_quat(q, normalize([-x for x in v]))

    t = 0
    while t < 1e6:
        lla = ecef2lla(*[v[i] + t*d[i] for i in range(3)], warn=False)
        if lla[2] < 1:
            return [*lla, quat2euler(q)[2]]
        t += max(lla[2] - 1, 0.1)