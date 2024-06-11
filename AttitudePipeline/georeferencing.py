import math
import numpy as np

FLATTENING = 1 / 298.257223563
R = 6378137

def ECEFtoLLA(x, y, z):
    '''
    Converts ECEF coordinates to latitude and longitude.
    https://www.mathworks.com/help/aeroblks/ecefpositiontolla.html
    '''
    long = math.atan(y / x)

    s = math.sqrt(x**2 + y**2)
    
    beta = math.atan(z / (s * (1 - FLATTENING))) # Reduced latitude

    e = math.sqrt(1 - (1 - FLATTENING)**2)
    
    num = lambda beta: z + e**2 * (1-FLATTENING) / (1 - e**2) * R * math.sin(beta)**3
    denom = lambda beta: s - e**2 * R * math.cos(beta)**3

    lat = math.atan(num(beta) / denom(beta))

    for _ in range(100): # TODO: Better convergence criteria, configurable threshold
        beta = math.atan((1 - FLATTENING) * math.tan(lat))
        lat = math.atan(num(beta) / denom(beta))

    N = R / math.sqrt(1 - e**2 * math.sin(lat)**2)
    alt = s*math.cos(lat) + (z + e**2 * N * math.sin(lat)) * math.sin(lat) - N

    return 180 + math.degrees(lat), 180 + math.degrees(long), alt


def applyQuat(q, v):
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

def earthIntersectCrit(x, y, z, tol = 1000):
    """
    Find if a vector lies on the earth ellipsoid.
    """
    return x**2/(6378.1370**2) + y**2/(6378.1370**2) + z**2/(6356.7523**2) - 1 < tol

def ang_from_vecs(v1: np.ndarray, v2:np.ndarray) -> float:
    """Takes two vectors v1, v2 as numpy arrays and returns the angle between them in degrees"""
    normv1, normv2 = np.linalg.norm(v1), np.linalg.norm(v2)
    ang = np.arccos(np.dot(v1,v2)/ (normv1 * normv2))
    return np.rad2deg(ang)

def georef(v, q):
    """
    Apply rotation and find latitude and longitude of intersection with Earth.
    """
    d = applyQuat(q, normalize(v))
    print(ang_from_vecs(v, d))
    def f(t):
        return [v[i] - t*d[i] for i in range(3)]

    t = 0
    while not earthIntersectCrit(*f(t), tol=0.002):
        t += 0.05
        if t > 10000:
            print("No convergence")
            return None
    
    return f(t)

import math

def quaternion_multiply(quaternion1, quaternion2):
    w1, x1, y1, z1 = quaternion1
    w2, x2, y2, z2 = quaternion2
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
    return [w, x, y, z]

def mrp2quat(m):
    """
    Modified Rodrigues Parameters to Quaternion
    """
    m = np.reshape(m, -1)
    magsq = np.dot(m, m)
    q = np.array([(1 - magsq), 2 * m[0], 2 * m[1], 2 * m[2]]) / (1 + magsq)
    return q

csv = np.genfromtxt('data/tensortech.csv', delimiter=',', skip_header=1) # TODO: Make more general, use existing classes maybe

# time,sigma_BN 1,sigma_BN 2,sigma_BN 3,omega_BN 1,omega_BN 2,omega_BN 3,torque 1,torque 2,torque 3,sigma_BR 1,sigma_BR 2,sigma_BR 3,omega_BR 1,omega_BR 2,omega_BR 3,r_BN_N 1,r_BN_N 2,r_BN_N 3

# Sigma_BN -> MRP Attitude

mrp = csv[:, 1:4]
qs = [mrp2quat(m) for m in mrp if not np.isnan(m).any()]
v = [824.005722, 450.648880, 6813.714020]
length = math.sqrt(sum([x**2 for x in v]))
print(length)

qx = [1/math.sqrt(2), -1/math.sqrt(2), 0, 0]
qy = [1/math.sqrt(2), 0, 1/math.sqrt(2), 0]
qz = [1/math.sqrt(2), 0, 0, 1/math.sqrt(2)]

write_csv = []

for i, q in enumerate(qs):
    print(i, q)
    ev = georef(v, quaternion_multiply(q, qx))
    if ev is not None:
        lla = ECEFtoLLA(*ev)
        print(lla)
        write_csv.append([i, *lla])

np.savetxt('georef.csv', write_csv, delimiter=',', fmt='%f')