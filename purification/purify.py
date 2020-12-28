from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA1
from Crypto.PublicKey import RSA
from config import APP_VERSION, UUID_PAYMENT, SESSION_ID, USER_ID, PRIV_KEY, AES_KEY
import msgpack, base64, datetime, random, logging, requests, time, urllib3

class BasicCrypto():
    def __init__(self):
        self.aes = AES_KEY

    def encrypt(self, payload):
        packed_request_content = msgpack.packb(payload)
        iv = packed_request_content[0:16]
        padded_request_content = pad(packed_request_content, 16)
        aes = AES.new(self.aes, AES.MODE_CBC, iv)
        encrypted_request_content = aes.encrypt(padded_request_content)
        return iv + encrypted_request_content

    def _decrypt_response(self, response_content):
        iv = response_content[0:16]
        aes = AES.new(self.aes, AES.MODE_CBC, iv)
        pad_text = aes.decrypt(response_content[16:])
        text = unpad(pad_text, 16)
        data_loaded = msgpack.unpackb(text)
        return data_loaded

class BaseAPI():
    URL = "https://api-sinoalice-us.pokelabo.jp"
    EXCESS_TRAFFIC = 14014

    def __init__(self):
        self.crypto = BasicCrypto()

        self.uuid_payment = UUID_PAYMENT
        self.priv_key = PRIV_KEY
        self.session_id = SESSION_ID
        self.user_id = USER_ID

        self.request_session = requests.session()
        self.request_session.verify = False
        urllib3.disable_warnings()

    def get_action_time(self, old_action_time=0):
        action_times = [0xfd2c030, 0x18c120b0, 0xdd98840, 0x13ee8a0, 0x1a26560, 0x21526d10, 0xe100190, 0xfbf3830]  # Todo how are those generated
        current_time = (datetime.datetime.utcnow() - datetime.datetime(1,1,1)).total_seconds() * 10**7
        time_offset = random.choice(action_times)
        next_time = int(current_time + time_offset)
        final_time = ((next_time & 0x3FFFFFFFFFFFFFFF) - 0x701CE1722770000)
        return final_time

    def _handle_response(self, response):
        decrypted_response = self.crypto._decrypt_response(response.content)
        logging.debug(f"from {response.request.path_url} {decrypted_response}")

        if decrypted_response.get("errors", None) is not None:
            if decrypted_response["errors"][0]["code"] == BaseAPI.EXCESS_TRAFFIC:
                logging.warning(f"EXCESS_TRAFFIC Exception {response.request.path_url}")
                raise ExcessTrafficException("")

        return decrypted_response

    def sign(self, data, hash_func, key):
        hashed_string = hash_func.new(data)
        base_string = base64.b64encode(hashed_string.digest())
        hashed_string = hash_func.new()
        hashed_string.update(base_string)
        signature = pkcs1_15.new(key).sign(hashed_string)
        return base64.b64encode(signature)

    def import_key(self, key):
        keyDER = base64.b64decode(key)
        keyPRIV = RSA.importKey(keyDER)
        return keyPRIV

    def _prepare_request(self, request_type, resource, inner_payload: dict):
        self.action_time = self.get_action_time()

        payload = {
            "payload": inner_payload,
            "uuid": self.uuid_payment,
            "userId": self.user_id,
            "sessionId": self.session_id,
            "actionToken": None,
            "ctag": None,
            "actionTime": self.action_time
        }

        logging.debug(f"to {request_type} {resource} {payload} {self.uuid_payment}")
        payload = self.crypto.encrypt(payload)

        key = self.import_key(self.priv_key)
        mac = self.sign(payload, SHA1, key).strip().decode()

        common_headers = {
            "Expect": "100-continue",
            "User-Agent": f"UnityRequest com.nexon.sinoalice {APP_VERSION} (Samsung Galaxy Note10)"
                          f" Android OS 10 / API-29)",
            "X-post-signature": f"{mac}",
            "X-Unity-Version": "2018.4.19f1",
            "Content-Type": "application/x-msgpack",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Cookie": f"PHPSESSID={self.session_id}",
            "Host": "api-sinoalice-us.pokelabo.jp"
        }

        self.request_session.headers = common_headers
        return payload

    def _post(self, resource, payload: dict = None) -> dict:
        url = BaseAPI.URL + resource

        payload = self._prepare_request("POST", resource, payload)

        resulting_response = None
        timeout_duration = 10 # todo exponential backoff
        while resulting_response is None:
            response = self.request_session.post(url, payload)
            try:
                resulting_response = self._handle_response(response)
            except ExcessTrafficException as e:
                time.sleep(timeout_duration)
                timeout_duration += 5
                if timeout_duration > 300:
                    logging.critical(f"Maximum attempts for {resource} aborting")
                    exit(-1)
        return resulting_response

class ExcessTrafficException(Exception):
    pass

class API(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)

    def POST__api_cleaning_check(self):
        payload = {}
        self._post("/api/cleaning/check", payload)

    def POST__api_cleaning_start(self, cleaning_type=1):
        payload = {
            "cleaningType": cleaning_type
        }
        response = self._post("/api/cleaning/start", payload)

        _data = response["payload"]["cleaningWaveData"]
        enemies = _data["normalEnemyCount"] + _data["rareEnemyCount"]
        wave = _data["nextWave"]
        ap = (_data["normalEnemyCount"] * _data["normalEnemyApRecoveryValue"]) + (_data["rareEnemyCount"] * _data["rareEnemyApRecoveryValue"])
        exp = (_data["normalEnemyCount"] * _data["normalEnemyExpValue"]) + (_data["rareEnemyCount"] * _data["rareEnemyExpValue"])

        return enemies, wave, ap, exp

    def POST__api_cleaning_end_wave(self, remain_time, current_wave, ap, exp, enemy_down):
        payload = {
            "remainTime": remain_time,
            "currentWave": current_wave,
            "getAp": ap,
            "getExp": exp,
            "getEnemyDown": enemy_down
        }
        response = self._post("/api/cleaning/end_wave", payload)

        _data = response["payload"]["cleaningWaveData"]
        enemies = _data["normalEnemyCount"] + _data["rareEnemyCount"]
        wave = _data["nextWave"]
        ap = (_data["normalEnemyCount"] * _data["normalEnemyApRecoveryValue"]) + (_data["rareEnemyCount"] * _data["rareEnemyApRecoveryValue"])
        exp = (_data["normalEnemyCount"] * _data["normalEnemyExpValue"]) + (_data["rareEnemyCount"] * _data["rareEnemyExpValue"])

        return enemies, wave, ap, exp

    def POST__api_cleaning_end(self, end_wave):
        payload = {
            "remainTime": 0,
            "currentWave": end_wave,
            "getAp": 0,
            "getExp": 0,
            "getEnemyDown": 0
        }
        self._post("/api/cleaning/end", payload)

    def POST__api_cleaning_retire(self):
        payload = {}
        self._post("/api/cleaning/retire", payload)

class Purification():
    def __init__(self):
        self.api = API()

    def run(self):
        self.api.POST__api_cleaning_check()
        remaining = 29
        enemies, wave, ap, exp = self.api.POST__api_cleaning_start(2)
        while remaining >= 0:
            enemies, wave, ap, exp = self.api.POST__api_cleaning_end_wave(remaining, wave, ap, exp, enemies)
            population = [1, 2]
            weight = [0.3, 0.7]
            rn = random.choices(population, weight)[0]
            remaining -= rn
            time.sleep(rn)
        self.api.POST__api_cleaning_end(wave)

Purification().run()