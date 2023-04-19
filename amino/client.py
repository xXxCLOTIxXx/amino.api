from .utils.requester import Requester
from .utils.helpers import Generator
from .utils import objects
from .socket import SocketHandler, Callbacks

from time import time as timestamp
from json import loads, dumps
from requests import Session
from typing import Union


class Client(SocketHandler, Callbacks):
	def __init__(self, socket_enabled: bool = True, socket_debug: bool = False, socket_trace: bool = False,  auto_device: bool = False, deviceId: str = None, proxies: dict = None, certificatePath = None):
		self.proxies = proxies
		self.certificatePath = certificatePath
		self.session = Session()
		self.profile = objects.profile()
		self.req = Requester(session=self.session, deviceId=deviceId, auto_device=auto_device)
		self.socket_enabled = socket_enabled

		SocketHandler.__init__(self, self.req, socket_trace, socket_debug)
		Callbacks.__init__(self)




	def login(self, email: str, password: str = None, secret: str = None):
		data = dumps({
			"email": email,
			"v": 2,
			"secret": secret if secret else f"0 {password}",
			"deviceID": self.req.gen.get_headers(deviceId=self.req.deviceId).get("NDCDEVICEID"),
			"clientType": 100,
			"action": "normal",
			"timestamp": int(timestamp() * 1000)
		})

		response = self.req.make_request(method="POST", endpoint="/g/s/auth/login", body=data, proxies=self.proxies, verify=self.certificatePath)
		json = loads(response.text)
		self.profile = objects.profile(json)
		self.req._set(1, self.profile.sid)
		if self.socket_enabled:self.connect()

		return self.profile


	def login_phone(self, phone: str, password: str):
		data = dumps({
			"phoneNumber": phone,
			"v": 2,
			"secret": f"0 {password}",
			"deviceID": self.req.gen.get_headers(deviceId=self.req.deviceId).get("NDCDEVICEID"),
			"clientType": 100,
			"action": "normal",
			"timestamp": int(timestamp() * 1000)
		})

		response = self.req.make_request(method="POST", endpoint="/g/s/auth/login", body=data, proxies=self.proxies, verify=self.certificatePath)
		json = loads(response.text)
		self.profile = objects.profile(json)
		self.req._set(1, self.profile.sid)
		if self.socket_enabled:self.connect()
		return self.profile



	def logout(self):

		data = dumps({
		"deviceID": self.req.gen.get_headers(deviceId=self.req.deviceId).get("NDCDEVICEID"),
		"clientType": 100,
		"timestamp": int(timestamp() * 1000)
		})
		response = self.req.make_request(method="POST", endpoint="/g/s/auth/logout", body=data, proxies=self.proxies, verify=self.certificatePath)
		self.req.sid = None
		self.profile = objects.profile()
		if self.socket_enabled:self.close()
		return response.status_code



	def join_voice_chat(self, comId: Union[int, str], chatId: str, joinType: int = 1):

		data = {
			"o": {
				"ndcId": int(comId),
				"threadId": chatId,
				"joinRole": joinType,
				"id": "2154531"
			},
			"t": 112
		}
		data = dumps(data)
		self.send(data)

	def join_video_chat(self, comId: Union[int, str], chatId: str, joinType: int = 1):

		data = {
			"o": {
				"ndcId": int(comId),
				"threadId": chatId,
				"joinRole": joinType,
				"channelType": 5,
				"id": "2154531"
			},
			"t": 108
		}
		data = dumps(data)
		self.send(data)




	def get_from_link(self, link: str):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/link-resolution?q={link}", proxies=self.proxies, verify=self.certificatePath)
		return objects.linkInfo(loads(response.text).get("linkInfoV2"))


	def join_community(self, comId: Union[int, str], invitationId: str = None):

		data = {"timestamp": int(timestamp() * 1000)}
		if invitationId: data["invitationId"] = invitationId
		response = self.req.make_request(method="POST", endpoint=f"/x{comId}/s/community/join", body=dumps(data), proxies=self.proxies, verify=self.certificatePath)
		return response.status_code


	def request_join_community(self, comId: Union[int, str], message: str = None):

		data = dumps({"message": message, "timestamp": int(timestamp() * 1000)})
		response = self.req.make_request(method="POST", endpoint=f"/x{comId}/s/community/membership-request", body=data, proxies=self.proxies, verify=self.certificatePath)
		return response.status_code


	def leave_community(self, comId: Union[int, str]):

		response = self.req.make_request(method="POST", endpoint=f"/x{comId}/s/community/leave", proxies=self.proxies, verify=self.certificatePath)
		return response.status_code

	def join_chat(self, chatId: str):

		response = self.req.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/member/{self.profile.userId}", type="application/x-www-form-urlencoded", proxies=self.proxies, verify=self.certificatePath)
		return response.status_code

	def leave_chat(self, chatId: str):

		response = self.req.make_request(method="DELETE", endpoint=f"/g/s/chat/thread/{chatId}/member/{self.profile.userId}", proxies=self.proxies, verify=self.certificatePath)
		return response.status_code