from .utils.requester import Requester
from .utils.helpers import Generator
from .utils import objects, exceptions
from .socket import SocketHandler, Callbacks

from time import time as timestamp
from json import loads, dumps
from requests import Session
from typing import Union, BinaryIO
from base64 import b64encode
from json_minify import json_minify
from uuid import uuid4
from io import BytesIO

class Client(SocketHandler, Callbacks):
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


	def login_sid(self, sid: str):
		self.profile = objects.profile({"sid": sid, "auid": self.req.gen.sid_to_uid(sid)})
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

	def join_chat(self, chatId: str):

		response = self.req.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/member/{self.profile.userId}", type="application/x-www-form-urlencoded")
		return response.status_code

	def leave_chat(self, chatId: str):

		response = self.req.make_request(method="DELETE", endpoint=f"/g/s/chat/thread/{chatId}/member/{self.profile.userId}")
		return response.status_code


	def send_message(self, chatId: str, message: str = None, messageType: int = 0, file: BinaryIO = None, fileType: str = None, replyTo: str = None, mentionUserIds: list = None, stickerId: str = None, embedId: str = None, embedType: int = None, embedLink: str = None, embedTitle: str = None, embedContent: str = None, embedImage: BinaryIO = None):

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


		response = self.req.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/message", body=dumps(data))
		return response.status_code

	def send_video(self, chatId: str, message: str = None, videoFile: BytesIO = None, imageFile: BytesIO = None, mediaUhqEnabled: bool = False):
		
		filename = str(uuid4()).upper()
		сover, video = f"{filename}_thumb.jpg", f"{filename}.mp4"
		
		data = {
			"clientRefId": int(timestamp() / 10 % 1000000000),
			"content": message,
			"mediaType": 123,
			"videoUpload":
			{
				"contentType": "video/mp4",
				"cover": сover,
				"video": video
			},
			"type": 4,
			"timestamp": int(timestamp() * 1000),
			"mediaUhqEnabled": mediaUhqEnabled,
			"extensions": {}	
		}
		
		files = {
			video: (video, videoFile.read(), 'video/mp4'),
			сover: (сover, imageFile.read(), 'application/octet-stream'),
			'payload': (None, data, 'application/octet-stream')
		}
		
		response = self.req.make_request(
			method="POST",
			endpoint=f"/g/s/chat/thread/{chatId}/message",
			payload=dumps(data),
			files=files
		)
		
		return response.status_code

	def delete_message(self, chatId: str, messageId: str, asStaff: bool = False, reason: str = None):

		if asStaff:
			data = dumps({
				"adminOpName": 102,
				"adminOpNote": {"content": reason},
				"timestamp": int(timestamp() * 1000)
			})

			response = self.req.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/message/{messageId}/admin", body=data)
			return response.status_code			

		response = self.req.make_request(method="DELETE", endpoint=f"/g/s/chat/thread/{chatId}/message/{messageId}")
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


	def send_active_obj(self, comId: str, tz: int = None, timers: list = None):
		#TODO
		data = json_minify(dumps({"userActiveTimeChunkList": timers if timers else self.req.gen.timers(), "timestamp": int(timestamp() * 1000), "optInAdsFlags": 2147483647, "timezone": tz if tz else self.req.gen.timezone()}))
		response = self.req.make_request(method="POST", endpoint=f"/x{comId}/s/community/stats/user-active-time", body=data)
		return response.status_code


	def request_verify_code(self, email: str, resetPassword: bool = False):

		data = {
			"identity": email,
			"type": 1,
			"deviceID": self.req.gen.get_headers(deviceId=self.req.deviceId).get("NDCDEVICEID")
		}

		if resetPassword:
			data["level"] = 2
			data["purpose"] = "reset-password"


		response = self.req.make_request(method="POST", endpoint=f"/g/s/auth/request-security-validation", body=dumps(data))
		return response.status_code


	def register(self, nickname: str, email: str, password: str, verificationCode: str, deviceId: str = None):

		data = dumps({
			"secret": f"0 {password}",
			"deviceID": self.req.gen.get_headers(deviceId=self.req.deviceId).get("NDCDEVICEID"),
			"email": email,
			"clientType": 100,
			"nickname": nickname,
			"latitude": 0,
			"longitude": 0,
			"address": None,
			"clientCallbackURL": "narviiapp://relogin",
			"validationContext": {
				"data": {
					"code": verificationCode
				},
				"type": 1,
				"identity": email
			},
			"type": 1,
			"identity": email,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.req.make_request(method="POST", endpoint=f"/g/s/auth/register", body=data)
		return loads(response.text)



	def verify_account(self, email: str, code: str):

		data = dumps({
			"validationContext": {
				"type": 1,
				"identity": email,
				"data": {"code": code}},
			"deviceID": self.device_id,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.req.make_request(method="POST", endpoint=f"/g/s/auth/check-security-validation", body=data)
		return response.status_code


	def delete_account(self, password: str):

		data = dumps({
			"deviceID": self.req.gen.get_headers(deviceId=self.req.deviceId).get("NDCDEVICEID"),
			"secret": f"0 {password}"
		})
		response = self.req.make_request(method="POST", endpoint=f"/g/s/account/delete-request", body=data)
		return response.status_code




	def restore_account(self, email: str, password: str):

		data = dumps({
			"secret": f"0 {password}",
			"deviceID": self.req.gen.get_headers(deviceId=self.req.deviceId).get("NDCDEVICEID"),
			"email": email,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.req.make_request(method="POST", endpoint=f"/g/s/account/delete-request/cancel", body=data)
		return response.status_code


	def activate_account(self, email: str, code: str):

		data = dumps({
			"type": 1,
			"identity": email,
			"data": {"code": code},
			"deviceID": self.req.gen.get_headers(deviceId=self.req.deviceId).get("NDCDEVICEID")
		})

		response = self.req.make_request(method="POST", endpoint=f"/g/s/auth/activate-email", body=data)
		return response.status_code


	def configure_gender(self, age: int, gender: str):

		if gender.lower() == "male": gender = 1
		elif gender.lower() == "female": gender = 2
		elif gender.lower() == "non-binary": gender = 255
		else: raise exceptions.IncorrectType(gender)
		if age <= 12: raise exceptions.AgeTooLow(age)

		data = dumps({
			"age": age,
			"gender": gender,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.req.make_request(method="POST", endpoint=f"/g/s/persona/profile/basic", body=data)
		return response.status_code


	def change_password(self, email: str, password: str, code: str):
		deviceId = self.req.gen.get_headers(deviceId=self.req.deviceId).get("NDCDEVICEID")

		data = dumps({
			"updateSecret": f"0 {password}",
			"emailValidationContext": {
				"data": {
					"code": code
				},
				"type": 1,
				"identity": email,
				"level": 2,
				"deviceID": deviceId
			},
			"phoneNumberValidationContext": None,
			"deviceID": deviceId
		})


		response = self.req.make_request(method="POST", endpoint=f"/g/s/auth/reset-password", body=data)
		return response.status_code


	def get_eventlog(self, language: str = "en"):
		response = self.req.make_request(method="GET", endpoint=f"/g/s/eventlog/profile?language={language.lower()}")
		return loads(response.text)


	def get_my_communities(self, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/community/joined?v=1&start={start}&size={size}")
		return objects.communityList(loads(response.text)["communityList"])


	def get_profile_in_communities(self, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/community/joined?v=1&start={start}&size={size}")
		return loads(response.text)["userInfoInCommunities"]


	def get_user_info(self, userId: str):


		response = self.req.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}")
		return objects.UserProfile(loads(response.text)["userProfile"])


	def get_chat_threads(self, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/chat/thread?type=joined-me&start={start}&size={size}")
		return objects.ThreadList(loads(response.text)["threadList"])


	def get_chat_thread(self, chatId: str):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/chat/thread/{chatId}")
		return objects.ThreadList(loads(response.text)["thread"])


	def get_chat_members(self, chatId: str, start: int = 0, size: int = 25, type: str = "default"):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/chat/thread/{chatId}/member?start={start}&size={size}&type={type}&cv=1.2")
		return objects.userProfileList(loads(response.text)["memberList"])



	def start_chat(self, userId: Union[str, list], message: str, title: str = None, content: str = None, isGlobal: bool = False, publishToGlobal: bool = False):

		if isinstance(userId, str): userIds = [userId]
		elif isinstance(userId, list): userIds = userId
		else: raise exceptions.IncorrectType(type(userId))

		data = {
			"title": title,
			"inviteeUids": userIds,
			"initialMessageContent": message,
			"content": content,
			"timestamp": int(timestamp() * 1000)
		}

		if isGlobal: data["type"] = 2; data["eventSource"] = "GlobalComposeMenu"
		else: data["type"] = 0

		if publishToGlobal: data["publishToGlobal"] = 1
		else: data["publishToGlobal"] = 0

		response = self.req.make_request(method="POST", endpoint=f"/g/s/chat/thread", body=dumps(data))
		return objects.Thread(loads(response.text)["thread"])



	def invite_to_chat(self, userId: Union[str, list], chatId: str):

		if isinstance(userId, str): userIds = [userId]
		elif isinstance(userId, list): userIds = userId
		else: raise exceptions.IncorrectType(type(userId))

		data = dumps({
			"uids": userIds,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.req.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/member/invite", body=data)
		return response.status_code



	def kick(self, userId: str, chatId: str, allowRejoin: bool = True):

		response = self.req.make_request(method="DELETE", endpoint=f"/g/s/chat/thread/{chatId}/member/{userId}?allowRejoin={1 if allowRejoin else 0}")
		return response.status_code


	def get_chat_messages(self, chatId: str, size: int = 25, pageToken: str = None):

		response = self.req.make_request(method="GET",
			endpoint=f"/g/s/chat/thread/{chatId}/message?v=2&pagingType=t&size={size}{f'&pageToken={pageToken}' if pageToken else ''}")
		return objects.MessageList(loads(response.text))


	def get_message_info(self, chatId: str, messageId: str):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/chat/thread/{chatId}/message/{messageId}")
		return objects.Message(loads(response.text)["message"])


	def get_community_info(self, comId: str):

		response = self.req.make_request(method="GET", endpoint=f"/g/s-x{comId}/community/info?withInfluencerList=1&withTopicList=true&influencerListOrderStrategy=fansCount")
		return objects.CommunityInfo(loads(response.text)["community"])


	def search_community(self, aminoId: str):
		#TODO

		response = self.req.make_request(method="GET", endpoint=f"/g/s/search/amino-id-and-link?q={aminoId}")
		return response.text


	def get_user_following(self, userId: str, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}/joined?start={start}&size={size}")
		return objects.userProfileList(loads(response.text))


	def get_user_followers(self, userId: str, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}/member?start={start}&size={size}")
		return objects.userProfileList(loads(response.text))



	def get_user_visitors(self, userId: str, start: int = 0, size: int = 25):
		#TODO

		response = self.req.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}/visitors?start={start}&size={size}")
		return loads(response.text)


	def get_blocked_users(self, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/block?start={start}&size={size}")
		return objects.userProfileList(loads(response.text))