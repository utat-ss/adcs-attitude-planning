from .consts import R, FLATTENING, E2
import numpy as np
import math

def mrp2quat(m):
    """
    Modified Rodrigues Parameters to Quaternion
    """
    m = np.reshape(m, -1)
    magsq = np.dot(m, m)
    q = np.array([(1 - magsq), 2 * m[0], 2 * m[1], 2 * m[2]]) / (1 + magsq)
    return q.tolist()

def ecef2lla(x, y, z, warn = True):
    '''
    Converts ECEF coordinates to latitude, longitude, and altitude.
    https://www.mathworks.com/help/aeroblks/ecefpositiontolla.html
    '''

    if x < 1e6 and warn:
        print("WARNING: This function expects ECEF coordinates in meters. You may have passed ECEF coordinates in kilometers.")

    lon = math.atan2(y, x)

    s = math.sqrt(x**2 + y**2)
    beta = math.atan(z / (1 - FLATTENING) / s)

    lat_old = 0
    while True:
        lat = math.atan((z + E2 * R * math.sin(beta)**3) / (s - E2 * R * math.cos(beta)**3))
        if abs(lat - lat_old) < 1e-12:
            break
        lat_old = lat
        beta = math.atan((1 - FLATTENING) * math.tan(lat))
    
    N = R / math.sqrt(1 - E2 * math.sin(lat)**2)
    alt = s * math.cos(lat) + (z + E2 * N * math.sin(lat)) * math.sin(lat) - N

    lat = math.degrees(lat)
    lon = math.degrees(lon)

    return lat, lon, alt

def quat2euler(q):
    w, x, y, z = q
    ysqr = y * y

    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + ysqr)
    X = np.degrees(np.arctan2(t0, t1))

    t2 = +2.0 * (w * y - z * x)
    t2 = np.where(t2>+1.0,+1.0,t2)

    t2 = np.where(t2<-1.0, -1.0, t2)
    Y = np.degrees(np.arcsin(t2))

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (ysqr + z * z)
    Z = np.degrees(np.arctan2(t3, t4))

    return X, Y, Z 