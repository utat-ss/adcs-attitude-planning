import math
import numpy as np
import geopy.distance
from .convert import ecef2lla, quat2euler
from scipy.spatial.transform import Rotation as R
from scipy.spatial.transform import Slerp
import datetime

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

def vec_diff(v1, v2):
    return [v1[i] - v2[i] for i in range(3)]

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
        
def georef_ana(v, q):
    R = 6378137
    d = apply_quat(q, normalize([-x for x in v]))
    
    a = np.dot(d, d)
    b = 2 * np.dot(v, d)
    c = np.dot(v, v) - R**2

    disc = b**2 - 4*a*c
    if disc < 0:
        return None
    elif disc == 0:
        t = (-b)/(2*a)
    else:
        t1 = (-b - np.sqrt(disc)) / (2*a)
        t2 = (-b + np.sqrt(disc)) / (2*a)
        t = min(t1, t2) if min(t1, t2) >= 0 else max(t1, t2)
    intersection_lla = ecef2lla(*[v[i] + t*d[i] for i in range(3)])
    return [*intersection_lla, quat2euler(q)[2]]


def interpolate_vectors(v1, v2, steps):
    return [[v1[i] + (v2[i] - v1[i]) * t for i in range(3)] for t in np.linspace(0, 1, steps)]

def interpolate_orbit(orbit, substeps):
    res = [interpolate_vectors(orbit[i], orbit[i+1], substeps) for i in range(len(orbit) - 1)]
    return [item for sublist in res for item in sublist]

def quat_pow(q, n):
    angle = 2 * math.acos(q[0])
    new_angle = angle * n
    return [math.cos(new_angle / 2)] + [q[i] * math.sin(new_angle / 2) for i in range(1, 4)]

def interpolate_quaternions(q1, q2, steps):
    quats = np.array([q1, q2])
    r = R.from_quat(quats)
    slerp = Slerp([0, 1], r)
    return [list(slerp(t).as_quat()) for t in np.linspace(0, 1, steps)]

def interpolate_attitude(attitude, steps):
    res = [interpolate_quaternions(attitude[i], attitude[i+1], steps) for i in range(len(attitude) - 1)]
    return [item for sublist in res for item in sublist]

def interpolate_dates(dates, steps):
    res = [[dates[i] + datetime.timedelta(seconds=t) for t in np.linspace(0, (dates[i+1] - dates[i]).total_seconds(), steps)] for i in range(len(dates) - 1)]
    return [item for sublist in res for item in sublist]
    
def bearing(lat1, lon1, lat2, lon2):
    """
    Calculate the bearing between two lat, long points.
    """
    dLon = lon2 - lon1
    y = math.sin(dLon) * math.cos(lat2)
    x = math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dLon)
    brng = np.rad2deg(math.atan2(y, x))
    if brng < 0: brng+= 360
    return brng

def add_dist_to_lat_lon(lat, lon, dist, bearing):
    pt = geopy.distance.distance(meters=dist).destination((lat, lon), bearing)
    return (pt.latitude, pt.longitude)

def make_scanline(center_lat, center_long, next_lat, next_long, rotation, width_meters, height_meters):
    """
    Return the four corners of a rectangle in lat, long coordinates.
    """

    half_width = width_meters / 2
    half_height = height_meters / 2
    diag_dist = math.sqrt(half_width**2 + half_height**2)
    angle = math.atan(half_height / half_width)
    angle = math.degrees(angle)
    
    return [
        add_dist_to_lat_lon(center_lat, center_long, diag_dist, rotation + 90 - angle),
        add_dist_to_lat_lon(center_lat, center_long, diag_dist, rotation + 90 + angle),
        add_dist_to_lat_lon(center_lat, center_long, diag_dist, rotation - 90 - angle),
        add_dist_to_lat_lon(center_lat, center_long, diag_dist, rotation - 90 + angle)
    ]
