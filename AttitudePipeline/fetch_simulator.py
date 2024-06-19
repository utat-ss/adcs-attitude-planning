import requests
import json
import re
import time

def get_session(header):
    match = re.search(r'session=([^;]*)', header)
    return match.group(1) if match else None

def create_sim(name, tle_1, tle_2, span_min):
    url = "https://testingtyf.tensortech.co/platform-configuration"

    payload = json.dumps({
        "name": name,
        "adcs module": "999", # 10M
        "bus": {
            "size": 3, # 3U
            "type": 206, # No panels
            "content": [1,0,0,0,2,0,0,0,3,99] # TODO: MOI I think?
        },
        "orbit": {"content": [tle_1, tle_2]},
        "simulation option": {
            "maneuver": "3", # 1: Detumbling (AD), 2: Sun pointing, 3: Nadir, 4: Target (AD), 5: Fine (AD); AD -> Additional Data required to use mode
            "span": span_min, # minutes to run sim
            "step size": 1,
            "alignment axis": "6", # 1: +X, 2: -X, 3: +Y, 4: -Y, 5: +Z, 6: -Z
            "initial omega": 0, # initial angular velocity for detumbling
            "fine cmd": ["","","",""] # Quat for fine pointing
        }
    })

    headers = {'Content-Type': 'application/json'}

    response = requests.request("POST", url, headers=headers, data=payload)

    return get_session(response.headers['set-cookie'])

def progress(session):
    url = "https://testingtyf.tensortech.co/updateP"
    headers = {'Cookie': f'session={session}'}
    response = requests.request("GET", url, headers=headers)
    return float(response.json()['now'])


def wait_until_done(session):
    while True:
        p = progress(session)
        print(f"Progress: {int(p)}% [{'=' * int(p/10)}{' ' * (10 - int(p/10))}]")
        if p == 100:
            break
        time.sleep(1)
    time.sleep(5)

def extract_data(response_text, name):
    response_text = response_text[response_text.find(name) + 1:]
    response_text = response_text[response_text.find("'") + 1:]
    response_text = response_text[:response_text.find("'")]

    return json.loads(response_text)

def get_result(session):
    url = "https://testingtyf.tensortech.co/result"
    headers = {'Cookie': f'session={session}'}
    response = requests.request("GET", url, headers=headers)

    dataTypes = ["omegaData", "mrpData", "dipoleData", "gimbalAngData", "gimbalVecData", "wheelAccData", "wheelVecData", "attitudeErrorData", "desiredTorqueData"]
    res = {}
    for dataType in dataTypes:
        res[dataType] = extract_data(response.text, dataType)

    return res

from sgp4.api import Satrec, jday
import numpy as np

def date_str_to_jd(date_str):
    year = int(date_str[:4])
    month = int(date_str[5:7])
    day = int(date_str[8:10])
    hour = int(date_str[11:13])
    minute = int(date_str[14:16])
    second = int(date_str[17:19])
    return jday(year, month, day, hour, minute, second)

def tle_to_orbit(tle_1, tle_2, jd, fr):
    satellite = Satrec.twoline2rv(tle_1, tle_2)
    return satellite.sgp4_array(np.array([jd]), np.array([fr]))

def get_all_orbit_points(tle_1, tle_2, sim_data):
    new_data = []
    for data in sim_data["omegaData"]:
        jd, fr = date_str_to_jd(data["date"])
        e, r, v = tle_to_orbit(tle_1, tle_2, jd, fr)
        new_data.append({
            "date": data["date"],
            "e": e.tolist(),
            "r": r.tolist()[0],
            "v": v.tolist()[0]
        })
    return new_data

tle_1 = "1 47456U 21006AV  22146.88271796  .00014504  00000+0  76123-3 0  9993"
tle_2 = "2 47456  97.4467 206.6372 0010079   0.1840 359.9395 15.15793776 74006"

### General procedure for running a simulation
sid = create_sim("test", tle_1, tle_2, 5)
print(sid)
wait_until_done(sid)
res = get_result(sid)
res["orbit"] = get_all_orbit_points(tle_1, tle_2, res)

with open("sim_data.json", "w") as f:
    json.dump(res, f, indent=4)