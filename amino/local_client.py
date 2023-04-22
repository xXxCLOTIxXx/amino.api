from .utils.requester import Requester
from .utils.helpers import Generator
from .utils import objects, exceptions
from .client import Client

from time import time as timestamp
from json import loads, dumps
from requests import Session
from base64 import b64encode
from typing import BinaryIO, Union
from uuid import uuid4
from io import BytesIO

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
			endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message",
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

			response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}/admin", body=data)
			return response.status_code			

		response = self.req.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}")
		return response.status_code
		
	def post_poll(self, title: str, content: str, pollVariants: list, duration: int = 7, backgroundColor: str = None, imageForPollOptions: str = None) -> int:
		data = {
			"taggedBlogCategoryIdList": [],
			"content": content,
			"mediaList": None,
			"keywords": None,
			"eventSource": "GlobalComposeMenu",
			"title": title,
			"timestamp": int(timestamp() * 1000),
			"type": 4,
			"durationInDays": duration,
			"polloptList": [],
			"extensions": {
				"featuredType": 0,
				"style": {
					"coverMediaIndexList": None
				},
				"fansOnly": False,
				"pageSnippet": None,
				"quizPlayedTimes": 0,
				"__disabledLevel__": 0,
				"headlineStyle": None,
				"privilegeOfCommentOnPost": 0,
				"promotedTo": None,
				"quizTotalQuestionCount": 0,
				"promoteInfo": None,
				"promotedFrom": None,
				"pollSettings": {
					"polloptType": 0,
					"joinEnabled": False
				},
				"quizInBestQuizzes": False
			}
		}
		
		if len(pollVariants) < 2: raise Exception("2 poll options or bigger")
		for pollVariant in pollVariants:
			pollOpt = {
				"status": 0,
				"mediaList": [
					[
						100,
						imageForPollOptions,
						None,
						None,
						None,
						None
					]
				],
				"votedValue": 0,
				"globalVotedValue": 0,
				"parentType": 0,
				"title": str(pollVariant),
				"globalVotesCount": 0,
				"type": 0,
				"votesCount": 0,
				"refObjectType": 0,
				"votesSum": 0
			}
			if imageForPollOptions == None: pollOpt.pop("mediaList")
			data['polloptList'].append(pollOpt)

		response = self.req.make_request(
			method="POST",
			endpoint=f"/x{self.comId}/s/blog",
			body=dumps(data)
		)
		
		return response.status_code
		
	def post_blog(self, title: str, content: str, imageList: list = None, captionList: list = None, categoriesList: list = None, backgroundColor: str = None, fansOnly: bool = False, extensions: dict = None, crash: bool = False):
		mediaList = []

		if captionList is not None:
			for image, caption in zip(imageList, captionList):
				mediaList.append([100, self.upload_media(image, "image"), caption])

		else:
			if imageList is not None:
				for image in imageList:
					print(self.upload_media(image, "image"))
					mediaList.append([100, self.upload_media(image, "image"), None])

		data = {
			"address": None,
			"content": content,
			"title": title,
			"mediaList": mediaList,
			"extensions": extensions,
			"latitude": 0,
			"longitude": 0,
			"eventSource": "GlobalComposeMenu",
			"timestamp": int(timestamp() * 1000)
		}

		if fansOnly: data["extensions"] = {"fansOnly": fansOnly}
		if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
		if categoriesList: data["taggedBlogCategoryIdList"] = categoriesList

		response = self.req.make_request(
			method="POST",
			endpoint=f"/x{self.comId}/s/blog",
			body=dumps(data)
		)
		
		return response.status_code

	def post_wiki(self, title: str, content: str, icon: str = None, imageList: list = None, keywords: str = None, backgroundColor: str = None, fansOnly: bool = False):
		mediaList = []

		for image in imageList:
			mediaList.append([100, self.upload_media(image, "image"), None])

		data = {
			"label": title,
			"content": content,
			"mediaList": mediaList,
			"eventSource": "GlobalComposeMenu",
			"timestamp": int(timestamp() * 1000)
		}

		if icon: data["icon"] = icon
		if keywords: data["keywords"] = keywords
		if fansOnly: data["extensions"] = {"fansOnly": fansOnly}
		if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
		
		response = self.req.make_request(
			method="POST",
			endpoint=f"/x{self.comId}/s/item",
			body=dumps(data)
		)
		
		return response.status_code