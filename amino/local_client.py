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
			endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message",
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

			response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}/admin", body=data)
			return response.status_code			

		response = self.req.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}")
		return response.status_code
		
		
	def post_poll(self, comId: Union[str, int], title: str, content: str, pollVariants: list, duration: int = 7, backgroundColor: str = None, imageForPollOptions: str = None) -> int:

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
		
		response = self.req.make_request(method="POST", endpoint=f"/x{comId}/s/blog", body=dumps(data))
		return response.status_code


	def post_blog(self, comId: Union[str, int], title: str, content: str, imageList: list = None, captionList: list = None, categoriesList: list = None, backgroundColor: str = None, fansOnly: bool = False, extensions: dict = None, crash: bool = False):
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

		response = self.req.make_request(method="POST", endpoint=f"/x{comId}/s/blog", body=dumps(data))
		return response.status_code


	def post_wiki(self, comId: Union[str, int], title: str, content: str, icon: str = None, imageList: list = None, keywords: str = None, backgroundColor: str = None, fansOnly: bool = False):
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
		
		response = self.req.make_request(method="POST", endpoint=f"/x{comId}/s/item", body=dumps(data))
		return response.status_code
	

	def get_wiki_folders(self, comId: Union[str, int], folderId: str = None):
		fId = f"/{folderId}/item-previews" if folderId else ""
		
		response = self.req.make_request(method="GET", endpoint=f"/x{comId}/s/item-category{fId}")
		return self.objects.WikiFoldes(response.json())
	

	def get_all_approved_wikis(self, comId: Union[str, int], size: int = 10):
		response = self.req.make_request(method="GET", endpoint=f"/x{comId}/s/item?type=catalog-all&pagingType=t&size={size}")
		return response.json()


	def get_community_stickers(self, comId: Union[str, int], size: int = 25):
		response = self.req.make_request(method="GET", endpoint=f"/x{comId}/s/store/items?size={size}&sectionGroupId=sticker&storeGroupId=community-shared&pagingType=t")
		return response.json()
	

	def get_community_stickerpack(self, comId: Union[str, int], stickerId: str):
		response = self.req.make_request(method="GET", endpoint=f"/x{comId}/s/sticker-collection/{stickerId}?includeStickers=1")
		return response.json()
	

	def get_pending_wikis(self, comId: Union[str, int], size: int = 25):
		response = self.req.make_request(method="GET", endpoint=f"/x{comId}/s/knowledge-base-request?pagingType=t&size={size}&type=pending")
		return response.json()
	

	def reject_wiki(self, comId: Union[str, int], requestId: str):
		response = self.req.make_request(method="POST", endpoint=f"/x{comId}/s/knowledge-base-request/{requestId}/reject", body=dumps({ "timestamp": int(timestamp() * 1000) }))
		return response.status_code
	

	def approve_wiki(self, comId: Union[str, int], requestId: str, method: str = "replace"):
		base = { "timestamp": int(timestamp() * 1000) }
		if method in ['create', 'new']:
			base.update({"actionType": "create", "destinationCategoryIdList": []})
		elif method in ['replace', 'update']:
			base.update({"actionType": "replace"})
		else: raise Exception("invalid value of method")

		response = self.req.make_request(method="POST",endpoint=f"/x{comId}/s/knowledge-base-request/{requestId}/approve", body=dumps({ "timestamp": int(timestamp() * 1000) }))
		return response.status_code

	def get_flags(self, comId: Union[str, int], size: int = 25):
		response = self.req.make_request(method="GET", endpoint=f"/x{comId}/s/flag?size={size}&status=pending&type=all&pagingType=t")
		return response.json()
	

	def view_wiki(self, comId: Union[str, int], wikiId: str):
		response = self.req.make_request(method="GET", endpoint=f"/x{comId}/s/item/{wikiId}")
		return response.json()