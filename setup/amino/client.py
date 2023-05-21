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
from uuid import uuid4, UUID
from io import BytesIO
from binascii import hexlify
from os import urandom

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

	def upload_media(self, file: BinaryIO, fileType: str):

		if fileType == "audio":fileType = "audio/aac"
		elif fileType == "image":fileType = "image/jpg" 
		else: raise exceptions.IncorrectType(fileType)
		data = file.read()

		response = self.req.make_request(method="POST", endpoint="/g/s/media/upload", body=data, type=fileType)
		return loads(response.text)["mediaValue"]

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
		
		data = dumps({
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
		})
		
		files = {
			video: (video, videoFile.read(), 'video/mp4'),
			сover: (сover, imageFile.read(), 'application/octet-stream'),
			'payload': (None, data, 'application/octet-stream')
		}
		
		response = self.req.make_request(
			method="POST",
			endpoint=f"/g/s/chat/thread/{chatId}/message",
			payload=data,
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


	def get_my_chats(self, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/chat/thread?type=joined-me&start={start}&size={size}")
		return objects.ThreadList(loads(response.text)["threadList"])


	def get_chat_thread(self, chatId: str):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/chat/thread/{chatId}")
		return objects.Thread(loads(response.text)["thread"])


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

		response = self.req.make_request(method="GET",endpoint=f"/g/s/chat/thread/{chatId}/message?v=2&pagingType=t&size={size}{f'&pageToken={pageToken}' if pageToken else ''}")
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


	def get_blog_info(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None):

		if fileId:
			response = self.req.make_request(method="GET", endpoint=f"/g/s/block?start={start}&size={size}")
			return response.json()["file"]


		if blogId or quizId:
			url = f"/g/s/blog/{blogId if blogId else quizId}"
		elif wikiId:
			url = f"/g/s/blog/{wikiId}"
		else:
			raise exceptions.IncorrectType()

		response = self.req.make_request(method="GET", endpoint=url)
		return response.text


	def get_blog_comments(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, sorting: str = "newest", start: int = 0, size: int = 25):

		if sorting not in ["newest", "vote", "oldest"]: raise exceptions.IncorrectType(sorting)

		if blogId or quizId:
			url = f"/g/s/blog/{blogId if blogId else quizId}/comment?sort={sorting}&start={start}&size={size}"
		elif wikiId:
			url = f"/g/s/item/{wikiId}/comment?sort={sorting}&start={start}&size={size}"
		elif fileId:
			url = f"/g/s/shared-folder/files/{fileId}/comment?sort={sorting}&start={start}&size={size}"
		else:
			raise exceptions.IncorrectType()

		response = self.req.make_request(method="GET", endpoint=url)
		return response.json()["commentList"]


	def get_blocker_users(self, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/block/full-list?start={start}&size={size}")
		return response.json()["blockerUidList"]


	def get_wall_comments(self, userId: str, sorting: str, start: int = 0, size: int = 25):

		if sorting not in ["newest", "vote", "oldest"]: raise exceptions.IncorrectType(sorting)

		response = self.req.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}/g-comment?sort={sorting}&start={start}&size={size}")
		return response.json()["commentList"]



	def flag(self, reason: str, flagType: int, userId: str = None, blogId: str = None, wikiId: str = None, asGuest: bool = False):

		data = {
			"flagType": flagType,
			"message": reason,
			"timestamp": int(timestamp() * 1000)
		}
		if userId:
			data["objectId"] = userId
			data["objectType"] = 0
		elif blogId:
			data["objectId"] = blogId
			data["objectType"] = 1
		elif wikiId:
			data["objectId"] = wikiId
			data["objectType"] = 2
		else: raise exceptions.IncorrectType()
		response = self.req.make_request(method="POST", endpoint=f"/g/s/{'g-flag' if asGuest else 'flag'}", body=dumps(data))
		return response.status_code



	def mark_as_read(self, chatId: str, messageId: str):
		data = dumps({
			"messageId": messageId,
			"timestamp": int(timestamp() * 1000)
		})
		response = self.req.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/mark-as-read", body=data)
		return response.status_code

	def visit(self, userId: str):
		response = self.req.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}?action=visit")
		return response.status_code


	def send_coins(self, coins: int, blogId: str = None, chatId: str = None, objectId: str = None, transactionId: str = None):
		data = {
			"coins": coins,
			"tippingContext": {"transactionId": transactionId if transactionId else str(UUID(hexlify(urandom(16)).decode('ascii')))},
			"timestamp": int(timestamp() * 1000)
		}
		if blogId: url = f"/g/s/blog/{blogId}/tipping"
		elif chatId: url = f"/g/s/chat/thread/{chatId}/tipping"
		elif objectId:
			data["objectId"] = objectId
			data["objectType"] = 2
			url = f"/g/s/tipping"
		else: raise exceptions.IncorrectType()

		response = self.req.make_request(method="POST", endpoint=url, body=dumps(data))
		return response.status_code



	def follow(self, userId: Union[str, list]):

		if isinstance(userId, str):
			response = self.req.make_request(method="POST", endpoint=f"/g/s/user-profile/{userId}/member")
			return response.status_code

		elif isinstance(userId, list):
			response = self.req.make_request(method="POST", endpoint=f"/g/s/user-profile/{self.profile.userId}/joined", body=dumps({"targetUidList": userId, "timestamp": int(timestamp() * 1000)}))
			return response.status_code

		else:
			raise exceptions.IncorrectType(type(userId))



	def unfollow(self, userId: str):

		response = self.req.make_request(method="DELETE", endpoint=f"/g/s/user-profile/{self.profile.userId}/member/{userId}")
		return response.status_code

	def block(self, userId: str):

		response = self.req.make_request(method="POST", endpoint=f"/g/s/block/{userId}")
		return response.status_code



	def unblock(self, userId: str):

		response = self.req.make_request(method="DELETE", endpoint=f"/g/s/block/{userId}")
		return response.status_code



	def flag_community(self, comId: str, reason: str, flagType: int, isGuest: bool = False):


		data = dumps({
			"objectId": comId,
			"objectType": 16,
			"flagType": flagType,
			"message": reason,
			"timestamp": int(timestamp() * 1000)
		})
		response = self.req.make_request(method="POST", endpoint=f"/x{comId}/s/{'g-flag' if isGuest else 'flag'}", body=data)
		return response.status_code



	def edit_profile(self, nickname: str = None, content: str = None, icon: BinaryIO = None, backgroundColor: str = None, backgroundImage: str = None, defaultBubbleId: str = None):

		data = {
			"address": None,
			"latitude": 0,
			"longitude": 0,
			"mediaList": None,
			"eventSource": "UserProfileView",
			"timestamp": int(timestamp() * 1000)
		}

		if nickname: data["nickname"] = nickname
		if icon: data["icon"] = self.upload_media(icon, "image")
		if content: data["content"] = content
		if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
		if backgroundImage: data["extensions"] = {"style": {"backgroundMediaList": [[100, backgroundImage, None, None, None]]}}
		if defaultBubbleId: data["extensions"] = {"defaultBubbleId": defaultBubbleId}

		response = self.req.make_request(method="POST", endpoint=f"/g/s/user-profile/{self.profile.userId}", body=dumps(data))
		return response.status_code


	def set_privacy_status(self, isAnonymous: bool = False, getNotifications: bool = False):

		data = {"timestamp": int(timestamp() * 1000)}
		if isAnonymous: data["privacyMode"] = 2
		else: data["privacyMode"] = 1
		if getNotifications: data["privacyMode"] = 1
		else:data["notificationStatus"] = 2

		response = self.req.make_request(method="POST", endpoint=f"/g/s/account/visit-settings", body=dumps(data))
		return response.status_code


	def set_amino_id(self, aminoId: str):

		response = self.req.make_request(method="POST", endpoint=f"/g/s/account/change-amino-id", body=dumps({"aminoId": aminoId, "timestamp": int(timestamp() * 1000)}))
		return response.status_code



	def get_linked_communities(self, userId: str):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}/linked-community")
		return objects.communityList(response.json()["linkedCommunityList"])




	def get_unlinked_communities(self, userId: str):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/user-profile/{userId}/linked-community")
		return objects.communityList(response.json()["unlinkedCommunityList"])


	def reorder_linked_communities(self, comIds: list):

		response = self.req.make_request(method="POST", endpoint=f"/g/s/user-profile/{self.profile.userId}/linked-community/reorder", body=dumps({"ndcIds": comIds, "timestamp": int(timestamp() * 1000)}))
		return response.status_code


	def add_linked_community(self, comId: str):

		response = self.req.make_request(method="POST", endpoint=f"/g/s/user-profile/{self.profile.userId}/linked-community/{comId}")
		return response.status_code


	def remove_linked_community(self, comId: str):

		response = self.req.make_request(method="DELETE", endpoint=f"/g/s/user-profile/{self.profile.userId}/linked-community/{comId}")
		return response.status_code


	def comment(self, message: str, userId: str = None, blogId: str = None, wikiId: str = None, replyTo: str = None):

		data = {
			"content": message,
			"stickerId": None,
			"type": 0,
			"timestamp": int(timestamp() * 1000)
		}

		if replyTo: data["respondTo"] = replyTo

		if userId:
			data["eventSource"] = "UserProfileView"
			url = f"/g/s/user-profile/{userId}/g-comment"
		elif blogId:
			data["eventSource"] = "PostDetailView"
			url = f"/g/s/blog/{blogId}/g-comment"
		elif wikiId:
			data["eventSource"] = "PostDetailView"
			url = f"/g/s/item/{wikiId}/g-comment"
		else: raise exceptions.IncorrectType()

		response = self.req.make_request(method="POST", endpoint=url, body=dumps(data))
		return response.status_code


	def delete_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None):

		if userId: url = f"/g/s/user-profile/{userId}/g-comment/{commentId}"
		elif blogId: url = f"/g/s/blog/{blogId}/g-comment/{commentId}"
		elif wikiId: url = f"/g/s/item/{wikiId}/g-comment/{commentId}"
		else: raise exceptions.IncorrectType()

		response = self.req.make_request(method="DELETE", endpoint=url)
		return response.status_code


	def like_blog(self, blogId: Union[str, list] = None, wikiId: str = None):

		data = {
			"value": 4,
			"timestamp": int(timestamp() * 1000)
		}

		if blogId:
			if isinstance(blogId, str):
				data["eventSource"] = "UserProfileView"
				url = f"/g/s/blog/{blogId}/g-vote?cv=1.2"
			elif isinstance(blogId, list):
				data["targetIdList"] = blogId
				url = f"/g/s/feed/g-vote"
			else: raise exceptions.IncorrectType(type(blogId))

		elif wikiId:
			data["eventSource"] = "PostDetailView"			
			url = f"/g/s/item/{wikiId}/g-vote?cv=1.2"

		else: raise exceptions.IncorrectType()

		response = self.req.make_request(method="POST", endpoint=url, body=dumps(data))
		return response.status_code


	def unlike_blog(self, blogId: str = None, wikiId: str = None):

		if blogId: url = f"/g/s/blog/{blogId}/g-vote?eventSource=UserProfileView"
		elif wikiId: url = f"/g/s/item/{wikiId}/g-vote?eventSource=PostDetailView"
		else: raise exceptions.IncorrectType()

		response = self.req.make_request(method="DELETE", endpoint=url)
		return response.status_code


	def like_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None):

		data = {
			"value": 4,
			"timestamp": int(timestamp() * 1000)
		}

		if userId:
			data["eventSource"] = "UserProfileView"
			url = f"/g/s/user-profile/{userId}/comment/{commentId}/g-vote?cv=1.2&value=1"
		elif blogId:
			data["eventSource"] = "PostDetailView"
			url = f"/g/s/blog/{blogId}/comment/{commentId}/g-vote?cv=1.2&value=1"
		elif wikiId:
			data["eventSource"] = "PostDetailView"
			url = f"/g/s/item/{wikiId}/comment/{commentId}/g-vote?cv=1.2&value=1"
		else: raise exceptions.IncorrectType()

		response = self.req.make_request(method="POST", endpoint=url, body=dumps(data))
		return response.status_code


	def unlike_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None):

		if userId: url = f"/g/s/user-profile/{userId}/comment/{commentId}/g-vote?eventSource=UserProfileView"
		elif blogId: url = f"/g/s/blog/{blogId}/comment/{commentId}/g-vote?eventSource=PostDetailView"
		elif wikiId: url = f"/g/s/item/{wikiId}/comment/{commentId}/g-vote?eventSource=PostDetailView"
		else: raise exceptions.IncorrectType()

		response = self.req.make_request(method="DELETE", endpoint=url)
		return response.status_code

	def get_membership_info(self):

		response = self.req.make_request(method="GET", endpoint="/g/s/membership?force=true")
		return response.json()


	def get_ta_announcements(self, language: str = "en", start: int = 0, size: int = 25):

		if language not in self.get_supported_languages(): raise exceptions.UnsupportedLanguage(language)
		response = self.req.make_request(method="GET", endpoint=f"/g/s/announcement?language={language}&start={start}&size={size}")
		return response.json()["blogList"]


	def get_wallet_info(self):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/wallet")
		return response.json()["wallet"]



	def get_wallet_history(self, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/wallet/coin/history?start={start}&size={size}")
		return response.json()["coinHistoryList"]


	def get_from_deviceid(self, deviceId: str):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/auid?deviceId={deviceId}")
		return response.json()["auid"]


	def get_from_id(self, objectId: str, objectType: int, comId: str = None):

		data = json.dumps({
			"objectId": objectId,
			"targetCode": 1,
			"objectType": objectType,
			"timestamp": int(timestamp() * 1000)
		})

		if comId:
			url = f"/g/s-x{comId}/link-resolution"
		else:
			url = f"/g/s/link-resolution"
		response = self.req.make_request(method="GET", endpoint=url, body=data)
		return response.json()["linkInfoV2"]


	def get_supported_languages(self):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/community-collection/supported-languages?start=0&size=100", body=data)
		return response.json()["supportedLanguages"]


	def claim_new_user_coupon(self):

		response = self.req.make_request(method="POST", endpoint=f"/g/s/coupon/new-user-coupon/claim")
		return response.status_code


	def get_subscriptions(self, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/store/subscription?objectType=122&start={start}&size={size}")
		return response.json()["storeSubscriptionItemList"]


	def get_all_users(self, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/user-profile?type=recent&start={start}&size={size}")
		return response.json()


	def accept_host(self, chatId: str, requestId: str):

		response = self.req.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept", body=dumps({}))
		return response.status_code


	def link_identify(self, link: str):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/community/link-identify?q=http%3A%2F%2Faminoapps.com%2Finvite%2F{link}")
		return response.json()

	def invite_to_vc(self, chatId: str, userId: str):

		response = self.req.make_request(method="POST", endpoint=f"/g/s/chat/thread/{chatId}/vvchat-presenter/invite", body=dumps({"uid": userId}))
		return response.status_code


	def wallet_config(self, level: int):

		data = dumps({
			"adsLevel": level,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.req.make_request(method="POST", endpoint=f"/g/s/wallet/ads/config", body=data)
		return response.status_code



	def purchase(self, objectId: str, isAutoRenew: bool = False):
		data = dumps({
			"objectId": objectId,
			"objectType": 114,
			"v": 1,
			"paymentContext":
			{
				"discountStatus": 0,
				"isAutoRenew": isAutoRenew
			},
			"timestamp": timestamp()
		})

		response = self.req.make_request(method="POST", endpoint=f"/g/s/store/purchase", body=data)
		return response.status_code


	def get_public_communities(self, language: str = "en", size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/g/s/topic/0/feed/community?language={language}&type=web-explore&categoryKey=recommendation&size={size}&pagingType=t")
		return objects.communityList(response.json()["communityList"])


	def get_hall_of_fame(self, size: int = 25):
		response = self.req.make_request(method="GET", endpoint=f"/g/s/topic/0/feed/community?size={size}&categoryKey=customized&type=discover&pagingType=t&moduleId=23ce695c-c4da-4da5-a6c4-7777ba23b7aa")
		return response.json()
	
	def get_recommended_communities(self, size: int = 25):
		response = self.req.make_request(method="GET", endpoint=f"/g/s/topic/0/feed/community?size={size}&categoryKey=recommendation&type=discover&pagingType=t")
		return response.json()


	def edit_chat(self):
		pass