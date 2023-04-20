from .utils.requester import Requester
from .utils.helpers import Generator
from .utils import objects, exceptions
from .client import Client

from time import time as timestamp
from json import loads, dumps
from requests import Session
from base64 import b64encode
from typing import BinaryIO, Union


class LocalClient(Client):
	def __init__(self, comId: int, profile: objects.profile, deviceId: str = None, proxies: dict = None, certificatePath = None):
		self.profile = profile
		self.comId = comId
		Client.__init__(self, deviceId=deviceId, proxies=proxies, certificatePath=certificatePath)

	def join_chat(self, chatId: str):
		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}", type="application/x-www-form-urlencoded")
		return response.status_code

	def leave_chat(self, chatId: str):
		response = self.req.make_request(method="DELETE", endpoint=f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}")
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

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message", body=dumps(data))
		return response.status_code



	def delete_message(self, chatId: str, messageId: str, asStaff: bool = False, reason: str = None):

		if asStaff:
			data = dumps({
				"adminOpName": 102,
				"adminOpNote": {"content": reason},
				"timestamp": int(timestamp() * 1000)
			})

			response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}/admin", body=data)
			return response.status_code			

		response = self.req.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}")
		return response.status_code