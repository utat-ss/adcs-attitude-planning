import requests
import json
import re
import time
from enum import Enum
from sgp4.api import Satrec, jday
import numpy as np

class Maneuver(Enum):
    DETUMBLING = "1"
    SUN_POINTING = "2"
    NADIR = "3"
    TARGET_TRACKING = "4"
    FINE_POINTING = "5"

class AlignmentAxis(Enum):
    POS_X = "1"
    NEG_X = "2"
    POS_Y = "3"
    NEG_Y = "4"
    POS_Z = "5"
    NEG_Z = "6"

class SimulatonConfig:
    name: str
    adcs_module: str = "100" # 10m
    bus_size: int = 3 # 3U
    bus_type: int = 206 # No panels
    moi: list = [1,0,0,0,2,0,0,0,3]
    front_area: int = 99
    # bus_content: list = [1,0,0,0,2,0,0,0,3,99]
    # TLEs from
    tle_1: str = "1 47456U 21006AV  22146.88271796  .00014504  00000+0  76123-3 0  9993"
    tle_2: str = "2 47456  97.4467 206.6372 0010079   0.1840 359.9395 15.15793776 74006"
    maneuver: Maneuver
    sim_time_min: int
    step_size: float = 0.01
    alignment_axis: AlignmentAxis
    initial_omega: int = 0
    fine_cmd: list[str] = ["","","",""]

    def bus_content(self):
        return [*self.moi, self.front_area]

    def __init__(self, name, maneuver, sim_time_min, alignment_axis):
        self.name = name
        self.maneuver = maneuver
        self.sim_time_min = sim_time_min
        self.alignment_axis = alignment_axis
    
    def __str__(self):
        return f"Name: {self.name}, Maneuver: {self.maneuver}, Simulation Time: {self.sim_time_min} min, Alignment Axis: {self.alignment_axis}"

    @classmethod
    def from_json(self, data):
        if isinstance(data, str):
            data = json.loads(data)

        return SimulatonConfig(
            data["name"],
            Maneuver(data["simulation option"]["maneuver"]),
            data["simulation option"]["span"],
            AlignmentAxis(data["simulation option"]["alignment axis"])
        )

    def to_json(self):
        return json.dumps({
            "name": self.name,
            "adcs module": self.adcs_module,
            "bus": {
                "size": self.bus_size,
                "type": self.bus_type,
                "content": self.bus_content()
            },
            "orbit": {"content": [self.tle_1, self.tle_2]},
            "simulation option": {
                "maneuver": self.maneuver.value,
                "span": self.sim_time_min,
                "step size": self.step_size,
                "alignment axis": self.alignment_axis.value,
                "initial omega": self.initial_omega,
                "fine cmd": self.fine_cmd
            }
        })

class TensorTechSimulation:
    session: str = None
    simulation_config: SimulatonConfig
    omegaData: list
    mrpData: list
    dipoleData: list
    gimbalAngData: list
    gimbalVecData: list
    wheelAccData: list
    wheelVecData: list
    attitudeErrorData: list
    desiredTorqueData: list
    orbitData: list

    def __init__(self, simulation_config):
        self.simulation_config = simulation_config

    def __make_request(self, path, method, payload=None, vital=True):
        url = f"https://testingtyf.tensortech.co/{path}"
        headers = {'Cookie': f'session={self.session}'} if self.session else {'Content-Type': 'application/json'}
        response = requests.request(method, url, headers=headers, data=payload)

        if response.status_code != 200 and vital:
            print(f"Request failed with status code {response.status_code}")
            print(response.text)
            exit(1)

        return response
    
    def __get_session(self, header):
        match = re.search(r'session=([^;]*)', header)
        return match.group(1) if match else None

    def __init_session(self):
        response = self.__make_request("platform-configuration", "POST", self.simulation_config.to_json())
        self.session = self.__get_session(response.headers['set-cookie'])
    
    def __get_progress(self):
        response = self.__make_request("updateP", "GET", vital=False)
        return float(response.json()['now'])
    
    def __wait_until_done(self):
        while True:
            p = self.__get_progress()
            print(f"\rProgress: {int(p)}% [{'=' * int(p/10)}{' ' * (10 - int(p/10))}]", end='', flush=True)
            if p == 100:
                break
            time.sleep(1)
        time.sleep(5)
    
    def __extract_data(self, response_text, name):
        response_text = response_text[response_text.find(name) + 1:]
        response_text = response_text[response_text.find("'") + 1:]
        response_text = response_text[:response_text.find("'")]

        return json.loads(response_text)

    def __get_result(self):
        response = self.__make_request("result", "GET")
        dataTypes = ["omegaData", "mrpData", "dipoleData", "gimbalAngData", "gimbalVecData", "wheelAccData", "wheelVecData", "attitudeErrorData", "desiredTorqueData"]
        res = {}
        for dataType in dataTypes:
            # res[dataType] = self.__extract_data(response.text, dataType)
            self.__dict__[dataType] = self.__extract_data(response.text, dataType)
        return res
    
    def __date_str_to_jd(self, date_str):
        year = int(date_str[:4])
        month = int(date_str[5:7])
        day = int(date_str[8:10])
        hour = int(date_str[11:13])
        minute = int(date_str[14:16])
        second = int(date_str[17:19])
        return jday(year, month, day, hour, minute, second)
    
    def __tle_to_orbit(self, tle_1, tle_2, jd, fr):
        satellite = Satrec.twoline2rv(tle_1, tle_2)
        return satellite.sgp4_array(np.array([jd]), np.array([fr]))
    
    def __get_all_orbit_points(self, tle_1, tle_2):
        self.orbitData = []
        for data in self.gimbalAngData:
            jd, fr = self.__date_str_to_jd(data["date"])
            e, r, v = self.__tle_to_orbit(tle_1, tle_2, jd, fr)
            self.orbitData.append({
                "date": data["date"],
                "e": e.tolist(),
                "r": [x * 1000 for x in r.tolist()[0]],
                "v": v.tolist()[0]
            })

    def run(self):
        self.__init_session()
        self.__wait_until_done()
        self.__get_result()
        self.__get_all_orbit_points(self.simulation_config.tle_1, self.simulation_config.tle_2)

    def run_session_id(self, session_id):
        self.session = session_id
        self.__get_result()
        self.__get_all_orbit_points(self.simulation_config.tle_1, self.simulation_config.tle_2)

    @classmethod
    def from_file(self, filename):
        with open(filename, "r") as f:
            data = json.load(f)
            sim_config = SimulatonConfig.from_json(data["config"])
            sim = TensorTechSimulation(sim_config)
            sim.omegaData = data["omegaData"]
            sim.mrpData = data["mrpData"]
            sim.dipoleData = data["dipoleData"]
            sim.gimbalAngData = data["gimbalAngData"]
            sim.gimbalVecData = data["gimbalVecData"]
            sim.wheelAccData = data["wheelAccData"]
            sim.wheelVecData = data["wheelVecData"]
            sim.attitudeErrorData = data["attitudeErrorData"]
            sim.desiredTorqueData = data["desiredTorqueData"]
            sim.orbitData = data["orbitData"]
            return sim

    def save(self, filename):
        data = {}
        data["omegaData"] = self.omegaData
        data["mrpData"] = self.mrpData
        data["dipoleData"] = self.dipoleData
        data["gimbalAngData"] = self.gimbalAngData
        data["gimbalVecData"] = self.gimbalVecData
        data["wheelAccData"] = self.wheelAccData
        data["wheelVecData"] = self.wheelVecData
        data["attitudeErrorData"] = self.attitudeErrorData
        data["desiredTorqueData"] = self.desiredTorqueData
        data["orbitData"] = self.orbitData
        data["config"] = self.simulation_config.to_json()

        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

if __name__ == "__main__":
    sim = TensorTechSimulation(SimulatonConfig("Test", Maneuver.NADIR, 10, AlignmentAxis.POS_X))
    sim.run_session_id("177735af-016a-4839-b90d-bd6a9cd8d619")
    # sim.save("idr.json")