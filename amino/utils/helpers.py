from typing import Union
from hmac import new
from hashlib import sha1
from base64 import b64encode, urlsafe_b64decode
from json import loads, load, dump
from json.decoder import JSONDecodeError
from os import urandom
from time import time as timestamp
from time import strftime, gmtime
from uuid import uuid4


class Generator:
	def __init__(self, auto_device: bool = False):
		self.PREFIX = bytes.fromhex("19")
		self.SIG_KEY = bytes.fromhex("DFA5ED192DDA6E88A12FE12130DC6206B1251E44")
		self.DEVICE_KEY = bytes.fromhex("E7309ECC0953C6FA60005B2765F99DBBC965C8E9")
		self.auto_device = auto_device


	def signature(self, data: Union[str, bytes]):
		data = data if isinstance(data, bytes) else data.encode("utf-8")
		return b64encode(self.PREFIX + new(self.SIG_KEY, data, sha1).digest()).decode("utf-8")


	def generate_deviceId(self):
		ur = self.PREFIX + (urandom(20))
		mac = new(self.DEVICE_KEY, ur, sha1)
		return f"{ur.hex()}{mac.hexdigest()}".upper()



	def get_headers(self, data = None, content_type = None, sid: str = None, deviceId: str = None):
		saved_device = self.get_device()
		headers = {
			"NDCDEVICEID": self.generate_deviceId() if self.auto_device else deviceId if deviceId else saved_device.get("deviceId"),
			"NDCLANG": "ru",
			"Accept-Language": "ru-RU",
			"SMDEVICEID": "20230109055041eecd2b9dd8439235afe4522cb5dacd26011dba6bbfeeb752", 
			"User-Agent": saved_device.get("user_agent"),
			"Content-Type": "application/json; charset=utf-8",
			"Host": "service.narvii.com",
			"Accept-Encoding": "gzip",
			"Connection": "Upgrade"
		}
		if data:
			headers["Content-Length"] = str(len(data))
			headers["NDC-MSG-SIG"] = self.signature(data=data)
		if sid:          headers["NDCAUTH"] = f"sid={sid}"
		if content_type: headers["Content-Type"] = content_type
		if type == "==PAYLOAD==": headers.pop("Content-Type")
		
		return headers

	def get_ws_headers(self, final: str, sid: str = None, deviceId: str = None):
		return {
				"NDCDEVICEID": self.generate_deviceId() if self.auto_device else deviceId if deviceId else self.get_device().get("deviceId"),
				"NDCAUTH": f"sid={sid}",
				"NDC-MSG-SIG": self.signature(final)
			}

	@property
	def tapjoy_headers(self):
		return {
			"cookies": "__cfduid=d0c98f07df2594b5f4aad802942cae1f01619569096",
			"authorization": "Basic NWJiNTM0OWUxYzlkNDQwMDA2NzUwNjgwOmM0ZDJmYmIxLTVlYjItNDM5MC05MDk3LTkxZjlmMjQ5NDI4OA==",
			"X-Tapdaq-SDK-Version": "android-sdk_7.1.1",
			"Content-Type": "application/x-www-form-urlencoded",
			"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10; Redmi Note 9 Pro Build/QQ3A.200805.001; com.narvii.amino.master/3.4.33585)"
		}

	def tapjoy_data(self, userId: str):
		self.data = {
			"reward": {
				"ad_unit_id": "t00_tapjoy_android_master_checkinwallet_rewardedvideo_322",
				"credentials_type": "publisher",
				"custom_json": {
					"hashed_user_id": userId
				},
				"demand_type": "sdk_bidding",
				"event_id": str(uuid4()),
				"network": "tapjoy",
				"placement_tag": "default",
				"reward_name": "Amino Coin",
				"reward_valid": True,
				"reward_value": 2,
				"shared_id": "4d7cc3d9-8c8a-4036-965c-60c091e90e7b",
				"version_id": "1569147951493",
				"waterfall_id": "4d7cc3d9-8c8a-4036-965c-60c091e90e7b"
			},
			"app": {
				"bundle_id": "com.narvii.amino.master",
				"current_orientation": "portrait",
				"release_version": "3.4.33585",
				"user_agent": "Dalvik\/2.1.0 (Linux; U; Android 10; G8231 Build\/41.2.A.0.219; com.narvii.amino.master\/3.4.33567)"
			},
			"device_user": {
				"country": "US",
				"device": {
					"architecture": "aarch64",
					"carrier": {
						"country_code": 255,
						"name": "Vodafone",
						"network_code": 0
					},
					"is_phone": True,
					"model": "GT-S5360",
					"model_type": "Samsung",
					"operating_system": "android",
					"operating_system_version": "29",
					"screen_size": {
						"height": 2300,
						"resolution": 2.625,
						"width": 1080
					}
				},
				"do_not_track": False,
				"idfa": "0c26b7c3-4801-4815-a155-50e0e6c27eeb",
				"ip_address": "",
				"locale": "ru",
				"timezone": {
					"location": "Asia\/Seoul",
					"offset": "GMT+02:00"
				},
				"volume_enabled": True
			},
			"session_id": "7fe1956a-6184-4b59-8682-04ff31e24bc0",
			"date_created": 1633283996
		}




	def generate_device_info(self):
		return {
			"deviceId": self.generate_deviceId(),
			"user_agent": "Apple iPhone12,1 iOS v15.5 Main/3.12.2"
		}

	def get_device(self):
		try:
			with open("device_information.json", "r") as stream:
				data = load(stream)
		except (FileNotFoundError, JSONDecodeError):
			device = self.generate_device_info()
			with open("device_information.json", "w") as stream:
				dump(device, stream, indent=4)
			with open("device_information.json", "r") as stream:
				data = load(stream)
		return data


	def timezone(self):
		localhour = strftime("%H", gmtime())
		localminute = strftime("%M", gmtime())
		UTC = {
				"GMT0": '+0', "GMT1": '+60', "GMT2": '+120', "GMT3": '+180', "GMT4": '+240', "GMT5": '+300', "GMT6": '+360',
				"GMT7": '+420', "GMT8": '+480', "GMT9": '+540', "GMT10": '+600', "GMT11": '+660', "GMT12": '+720',
				"GMT13": '+780', "GMT-1": '-60', "GMT-2": '-120', "GMT-3": '-180', "GMT-4": '-240', "GMT-5": '-300',
				"GMT-6": '-360', "GMT-7": '-420', "GMT-8": '-480', "GMT-9": '-540', "GMT-10": '-600', "GMT-11": '-660'
		}

		hour = [localhour, localminute]
		if hour[0] == "00": tz = UTC["GMT-1"];return int(tz)
		if hour[0] == "01": tz = UTC["GMT-2"];return int(tz)
		if hour[0] == "02": tz = UTC["GMT-3"];return int(tz)
		if hour[0] == "03": tz = UTC["GMT-4"];return int(tz)
		if hour[0] == "04": tz = UTC["GMT-5"];return int(tz)
		if hour[0] == "05": tz = UTC["GMT-6"];return int(tz)
		if hour[0] == "06": tz = UTC["GMT-7"];return int(tz)
		if hour[0] == "07": tz = UTC["GMT-8"];return int(tz)
		if hour[0] == "08": tz = UTC["GMT-9"];return int(tz)
		if hour[0] == "09": tz = UTC["GMT-10"];return int(tz)
		if hour[0] == "10": tz = UTC["GMT13"];return int(tz)
		if hour[0] == "11": tz = UTC["GMT12"];return int(tz)
		if hour[0] == "12": tz = UTC["GMT11"];return int(tz)
		if hour[0] == "13": tz = UTC["GMT10"];return int(tz)
		if hour[0] == "14": tz = UTC["GMT9"];return int(tz)
		if hour[0] == "15": tz = UTC["GMT8"];return int(tz)
		if hour[0] == "16": tz = UTC["GMT7"];return int(tz)
		if hour[0] == "17": tz = UTC["GMT6"];return int(tz)
		if hour[0] == "18": tz = UTC["GMT5"];return int(tz)
		if hour[0] == "19": tz = UTC["GMT4"];return int(tz)
		if hour[0] == "20": tz = UTC["GMT3"];return int(tz)
		if hour[0] == "21": tz = UTC["GMT2"];return int(tz)
		if hour[0] == "22": tz = UTC["GMT1"];return int(tz)
		if hour[0] == "23": tz = UTC["GMT0"];return int(tz)



	def timers(self):
		return [
				{
					'start': int(timestamp()), 'end': int(timestamp()) + 300
				} for _ in range(50)
			]

	def decode_sid(self, SID: str):return loads(urlsafe_b64decode(SID + "=" * (4 - len(SID) % 4))[1:-20])

	def sid_to_uid(self, SID: str): return self.decode_sid(SID)["2"]

	def sid_to_ip_address(self, SID: str): return self.decode_sid(SID)["4"]

	def sid_created_time(self, SID: str): return self.decode_sid(SID)["5"]

	def sid_to_client_type(self, SID: str): return self.decode_sid(SID)["6"]