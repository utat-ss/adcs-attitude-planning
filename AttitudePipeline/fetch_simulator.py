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
            "maneuver": "2", # 1: Detumbling (AD), 2: Sun pointing, 3: Nadir, 4: Target (AD), 5: Fine (AD); AD -> Additional Data required to use mode
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

    print(response_text)

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

tle_1 = "1 47456U 21006AV  22146.88271797  .00014504  00000+0  76123-3 0  9993"
tle_2 = "2 47456  97.4467 206.6372 0010078   0.1840 359.9395 15.15793776 74006"
sid = create_sim("test", tle_1, tle_2, 2)
print(sid)
wait_until_done(sid)
get_result(sid)