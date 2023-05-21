from .utils.requester import Requester
from .utils.helpers import Generator
from .utils import objects, exceptions
from .socket import SocketHandler, Callbacks

from time import time as timestamp
from json import loads, dumps
from requests import Session
from typing import Union, BinaryIO
from base64 import b64encode


class FullClient(SocketHandler, Callbacks):
	def __init__(self, socket_enabled: bool = True, socket_debug: bool = False, socket_trace: bool = False,  auto_device: bool = False, deviceId: str = None, proxies: dict = None, certificatePath = None):
		self.session = Session()
		self.profile = objects.profile()
		self.req = Requester(session=self.session, deviceId=deviceId, auto_device=auto_device, proxies=proxies, verify=certificatePath)
		self.socket_enabled = socket_enabled

		SocketHandler.__init__(self, self.req, socket_trace, socket_debug)
		Callbacks.__init__(self)


	def set_proxies(self, proxies: Union[dict, str, None] = None):
		if isinstance(proxies, dict):self.req.proxies = proxies
		elif isinstance(proxies, str):self.req.proxies = {"http": proxies, "https": proxies}
		elif proxies is None:self.req.proxies = None
		else:raise exceptions.IncorrectType(type(proxies))

	def set_device_id(self, deviceId: str):
		self.req._set(2, deviceId)

	def set_sid(self, sid: str):
		self.req._set(1, sid)

	def upload_media(self, file: BinaryIO, fileType: str):

		if fileType == "audio":fileType = "audio/aac"
		elif fileType == "image":fileType = "image/jpg"
		else: raise exceptions.IncorrectType(fileType)
		data = file.read()

		response = self.req.make_request(method="POST", endpoint="/g/s/media/upload", body=data, type=fileType)
		return loads(response.text)["mediaValue"]


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

		response = self.req.make_request(method="POST", endpoint="/g/s/auth/login", body=data)
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

		response = self.req.make_request(method="POST", endpoint="/g/s/auth/login", body=data)
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
		response = self.req.make_request(method="POST", endpoint="/g/s/auth/logout", body=data)
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

		response = self.req.make_request(method="GET", endpoint=f"/g/s/link-resolution?q={link}")
		return objects.linkInfo(loads(response.text).get("linkInfoV2"))


	def join_community(self, comId: Union[int, str], invitationId: str = None):

		data = {"timestamp": int(timestamp() * 1000)}
		if invitationId: data["invitationId"] = invitationId
		response = self.req.make_request(method="POST", endpoint=f"/x{comId}/s/community/join", body=dumps(data))
		return response.status_code


	def request_join_community(self, comId: Union[int, str], message: str = None):

		data = dumps({"message": message, "timestamp": int(timestamp() * 1000)})
		response = self.req.make_request(method="POST", endpoint=f"/x{comId}/s/community/membership-request", body=data)
		return response.status_code


	def leave_community(self, comId: Union[int, str]):

		response = self.req.make_request(method="POST", endpoint=f"/x{comId}/s/community/leave")
		return response.status_code

	def join_chat(self, chatId: str, comId: Union[int, str] = None):
		if comId:
			response = self.req.make_request(method="POST", endpoint=f"/x{comId}/s/chat/thread/{chatId}/member/{self.profile.userId}", type="application/x-www-form-urlencoded")
			return response.status_code		

		response = self.req.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/member/{self.profile.userId}", type="application/x-www-form-urlencoded")
		return response.status_code

	def leave_chat(self, chatId: str, comId: Union[int, str] = None):
		if comId:
			response = self.req.make_request(method="DELETE", endpoint=f"{self.api}/x{comId}/s/chat/thread/{chatId}/member/{self.profile.userId}")
			return response.status_code		

		response = self.req.make_request(method="DELETE", endpoint=f"/g/s/chat/thread/{chatId}/member/{self.profile.userId}")
		return response.status_code



	def send_message(self, chatId: str, comId: Union[int, str] = None, message: str = None, messageType: int = 0, file: BinaryIO = None, fileType: str = None, replyTo: str = None, mentionUserIds: list = None, stickerId: str = None, embedId: str = None, embedType: int = None, embedLink: str = None, embedTitle: str = None, embedContent: str = None, embedImage: BinaryIO = None):

		if message and file is None:
			message = message.replace("<@", "‎‏").replace("@>", "‬‭")
		mentions = list()
		if mentionUserIds:
			for uid in mentionUserIds:
				mentions.append({"uid": uid})
		if embedImage:
			embedImage = [[100, self.upload_media(embedImage, "image"), None]]

		data = {
			"type": messageType,
			"content": message,
			"clientRefId": int(timestamp() / 10 % 1000000000),
			"attachedObject": {
				"objectId": embedId,
				"objectType": embedType,
				"link": embedLink,
				"title": embedTitle,
				"content": embedContent,
				"mediaList": embedImage
			},
			"extensions": {"mentionedArray": mentions},
			"timestamp": int(timestamp() * 1000)
		}

		if replyTo: data["replyMessageId"] = replyTo
		if stickerId:
			data["content"] = None
			data["stickerId"] = stickerId
			data["type"] = 3

		if file:
			data["content"] = None
			if fileType == "audio":
				data["type"] = 2
				data["mediaType"] = 110

			elif fileType == "image":
				data["mediaType"] = 100
				data["mediaUploadValueContentType"] = "image/jpg"
				data["mediaUhqEnabled"] = True

			elif fileType == "gif":
				data["mediaType"] = 100
				data["mediaUploadValueContentType"] = "image/gif"
				data["mediaUhqEnabled"] = True

			else: raise exceptions.IncorrectType(f"fileType: {fileType}")

			data["mediaUploadValue"] = b64encode(file.read()).decode()


		response = self.req.make_request(
				method="POST",
				endpoint=f"/x{comId}/s/chat/thread/{chatId}/message" if comId else f"/g/s/chat/thread/{chatId}/message",
				body=dumps(data)
			)
		return response.status_code


	def delete_message(self, chatId: str, messageId: str, comId: Union[int, str] = None, asStaff: bool = False, reason: str = None):

		if asStaff:
			data = dumps({
				"adminOpName": 102,
				"adminOpNote": {"content": reason},
				"timestamp": int(timestamp() * 1000)
			})

			response = self.req.make_request(method="POST", endpoint=f"/x{comId}/s/chat/thread/{chatId}/message/{messageId}/admin" if comId else f"/g/s/chat/thread/{chatId}/message/{messageId}/admin", body=data)
			return response.status_code			

		response = self.req.make_request(method="DELETE", endpoint=f"/x{comId}/s/chat/thread/{chatId}/message/{messageId}" if comId else f"/g/s/chat/thread/{chatId}/message/{messageId}")
		return response.status_code

	def get_public_communities(self, language: str = "en", size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/topic/0/feed/community?language={language}&type=web-explore&categoryKey=recommendation&size={size}&pagingType=t")
		return objects.communityList(loads(response.text))

	def get_all_users(self, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/user-profile?type=recent&start={start}&size={size}")
		return objects.userProfileList(loads(response.text))

	def get_wallet_info(self):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/wallet")
		return objects.Wallet(loads(response.text).get("wallet", {}))

	def get_wallet_history(self, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/wallet/coin/history?start={start}&size={size}")
		return objects.coinHistoryList(loads(response.text).get("coinHistoryList", {}))


	def watch_ad(self, userId: str = None):
		data = dumps(self.req.gen.tapjoy_data(userId if userId else self.profile.userId))
		response = self.req.session.request("POST", "https://ads.tapdaq.com/v4/analytics/reward", proxies=self.req.proxies, verify=self.req.verify, data=data, headers=self.req.gen.tapjoy_headers)
		return exceptions.check_exceptions(response.text) if response.status_code != 204 else response.status_code
