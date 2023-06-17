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
from time import timezone



class LocalClient(Client):
	def __init__(self, comId: Union[str,int] = None, profile: objects.profile = None, language: str = 'ru', deviceId: str = None, proxies: dict = None, certificatePath = None):
		self.profile = profile if profile else objects.profile()
		self.comId = comId
		Client.__init__(self, deviceId=deviceId, proxies=proxies, certificatePath=certificatePath,  language=language)


	def set_comId(self, comId: Union[str,int] = None):
		self.comId = comId
		return self.comId


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
		
		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/blog", body=dumps(data))
		return response.status_code


	def post_blog(self, title: str, content: str, imageList: list = None, captionList: list = None, categoriesList: list = None, backgroundColor: str = None, fansOnly: bool = False, extensions: dict = None, crash: bool = False):
		mediaList = list()

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

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/blog", body=dumps(data))
		return response.status_code


	def post_wiki(self, title: str, content: str, icon: str = None, imageList: list = None, keywords: str = None, backgroundColor: str = None, fansOnly: bool = False):
		mediaList = list()

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
		
		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/item", body=dumps(data))
		return response.status_code
	

	def get_wiki_folders(self, folderId: str = None):
		fId = f"/{folderId}/item-previews" if folderId else ""
		
		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/item-category{fId}")
		return objects.WikiFoldes(response.json())

	def get_all_approved_wikis(self, size: int = 10):
		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/item?type=catalog-all&pagingType=t&size={size}")
		return response.json()


	def get_community_stickers(self, size: int = 25):
		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/store/items?size={size}&sectionGroupId=sticker&storeGroupId=community-shared&pagingType=t")
		return response.json()
	

	def get_community_stickerpack(self, stickerId: str):
		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/sticker-collection/{stickerId}?includeStickers=1")
		return response.json()
	

	def get_pending_wikis(self, size: int = 25):
		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/knowledge-base-request?pagingType=t&size={size}&type=pending")
		return response.json()
	

	def reject_wiki(self, requestId: str):
		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/knowledge-base-request/{requestId}/reject", body=dumps({ "timestamp": int(timestamp() * 1000) }))
		return response.status_code
	

	def approve_wiki(self, requestId: str, method: str = "replace"):
		base = { "timestamp": int(timestamp() * 1000) }
		if method in ['create', 'new']:
			base.update({"actionType": "create", "destinationCategoryIdList": []})
		elif method in ['replace', 'update']:
			base.update({"actionType": "replace"})
		else: raise Exception("invalid value of method")

		response = self.req.make_request(method="POST",endpoint=f"/x{self.comId}/s/knowledge-base-request/{requestId}/approve", body=dumps({ "timestamp": int(timestamp() * 1000) }))
		return response.status_code

	def get_flags(self, size: int = 25):
		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/flag?size={size}&status=pending&type=all&pagingType=t")
		return response.json()
	

	def view_wiki(self, wikiId: str):
		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/item/{wikiId}")
		return response.json()



	def get_invite_codes(self, status: str = "normal", start: int = 0, size: int = 25):
		response = self.req.make_request(method="GET", endpoint=f"/g/s-x{self.comId}/community/invitation?status={status}&start={start}&size={size}")
		return response.json()["communityInvitationList"]


	def generate_invite_code(self, duration: int = 0, force: bool = True):
		data = dumps({
			"duration": duration,
			"force": force,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.req.make_request(method="POST", endpoint=f"/g/s-x{self.comId}/community/invitation", body=data)
		return response.json()["communityInvitation"]



	def delete_invite_code(self, inviteId: str):

		response = self.req.make_request(method="DELETE", endpoint=f"/g/s-x{self.comId}/community/invitation/{inviteId}")
		return response.status_code


	def get_vip_users(self):

		response = self.req.make_request(method="GET", endpoint=f"/{self.comId}/s/influencer")
		return objects.userProfileList(response.json()["userProfileList"])


	def edit_blog(self, blogId: str, title: str = None, content: str = None, imageList: list = None, categoriesList: list = None, backgroundColor: str = None, fansOnly: bool = False):
		
		mediaList = list()
		for image in imageList:
			mediaList.append([100, self.upload_media(image, "image"), None])

		data = {
			"address": None,
			"mediaList": mediaList,
			"latitude": 0,
			"longitude": 0,
			"eventSource": "PostDetailView",
			"timestamp": int(timestamp() * 1000)
		}

		if title: data["title"] = title
		if content: data["content"] = content
		if fansOnly: data["extensions"] = {"fansOnly": fansOnly}
		if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
		if categoriesList: data["taggedBlogCategoryIdList"] = categoriesList


		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/blog/{blogId}", body=dumps(data))
		return response.status_code



	def delete_blog(self, blogId: str):

		response = self.req.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/blog/{blogId}")
		return response.status_code



	def delete_wiki(self, wikiId: str):

		response = self.req.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/item/{wikiId}")
		return response.status_code



	def repost_blog(self, content: str = None, blogId: str = None, wikiId: str = None):
		if blogId: refObjectId, refObjectType = blogId, 1
		elif wikiId: refObjectId, refObjectType = wikiId, 2
		else: raise exceptions.IncorrectType()

		data = dumps({
			"content": content,
			"refObjectId": refObjectId,
			"refObjectType": refObjectType,
			"type": 2,
			"timestamp": int(timestamp() * 1000)
		})


		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/blog", body=data)
		return response.status_code


	def check_in(self, tz: int = -timezone // 1000):
		data = dumps({
			"timezone": tz,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/check-in", body=data)
		return response.status_code
		


	def repair_check_in(self, method: int = 0):
		data = {"timestamp": int(timestamp() * 1000)}
		if method == 0: data["repairMethod"] = "1"  # Coins
		elif method == 1: data["repairMethod"] = "2"  # Amino+
		else: raise exceptions.IncorrectType()
		data = dumps(data)

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/check-in/repair", body=data)
		return response.status_code



	def lottery(self, tz: int = -timezone // 1000):
		data = dumps({
			"timezone": tz,
			"timestamp": int(timestamp() * 1000)
		})
		

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/check-in/lottery", body=data)
		return response.json()["lotteryLog"]


	def edit_profile(self, nickname: str = None, content: str = None, icon: BinaryIO = None, chatRequestPrivilege: str = None, imageList: list = None, captionList: list = None, backgroundImage: str = None, backgroundColor: str = None, titles: list = None, colors: list = None, defaultBubbleId: str = None) -> int:
		mediaList = list()

		data = {"timestamp": int(timestamp() * 1000)}

		if captionList:
			for image, caption in zip(imageList, captionList):
				mediaList.append([100, self.upload_media(image, "image"), caption])
		else:
			if imageList:
				for image in imageList:
					mediaList.append([100, self.upload_media(image, "image"), None])
		if imageList or captionList:
			data["mediaList"] = mediaList


		if nickname: data["nickname"] = nickname
		if icon: data["icon"] = self.upload_media(icon, "image")
		if content: data["content"] = content

		if chatRequestPrivilege: data["extensions"] = {"privilegeOfChatInviteRequest": chatRequestPrivilege}
		if backgroundImage: data["extensions"] = {"style": {"backgroundMediaList": [[100, backgroundImage, None, None, None]]}}
		if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
		if defaultBubbleId: data["extensions"] = {"defaultBubbleId": defaultBubbleId}

		if titles or colors:
			tlt = list()
			for titles, colors in zip(titles, colors):
				tlt.append({"title": titles, "color": colors})

			data["extensions"] = {"customTitles": tlt}


		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/user-profile/{self.profile.userId}", body=dumps(data))
		return response.status_code


	def vote_poll(self, blogId: str, optionId: str) -> int:
		data = dumps({
			"value": 1,
			"eventSource": "PostDetailView",
			"timestamp": int(timestamp() * 1000)
		})

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/blog/{blogId}/poll/option/{optionId}/vote", body=data)
		return response.status_code



	def comment(self, message: str, userId: str = None, blogId: str = None, wikiId: str = None, replyTo: str = None, isGuest: bool = False) -> int:
		data = {
			"content": message,
			"stickerId": None,
			"type": 0,
			"timestamp": int(timestamp() * 1000)
		}

		if replyTo: data["respondTo"] = replyTo
		comType = "g-comment" if isGuest else "comment"

		if userId:
			data["eventSource"] = "UserProfileView"
			url = f"/x{self.comId}/s/user-profile/{userId}/{comType}"

		elif blogId:
			data["eventSource"] = "PostDetailView"
			url = f"/x{self.comId}/s/blog/{blogId}/{comType}"

		elif wikiId:
			data["eventSource"] = "PostDetailView"
			url = f"/x{self.comId}/s/item/{wikiId}/{comType}"

		else: raise exceptions.IncorrectType()
		response = self.req.make_request(method="POST", endpoint=url, body=dumps(data))
		return response.status_code



	def delete_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None) -> int:
		if userId: url = f"/x{self.comId}/s/user-profile/{userId}/comment/{commentId}"
		elif blogId: url = f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}"
		elif wikiId: url = f"/x{self.comId}/s/item/{wikiId}/comment/{commentId}"
		else: raise exceptions.IncorrectType()

		response = self.req.make_request(method="DELETE", endpoint=url)
		return response.status_code


	def like_blog(self, blogId: Union[str, list] = None, wikiId: str = None) -> int:

		data = {
			"value": 4,
			"timestamp": int(timestamp() * 1000)
		}

		if blogId:
			if isinstance(blogId, str):
				data["eventSource"] = "UserProfileView"
				url = f"/x{self.comId}/s/blog/{blogId}/vote?cv=1.2"

			elif isinstance(blogId, list):
				data["targetIdList"] = blogId
				url = f"/x{self.comId}/s/feed/vote"

			else: raise exceptions.IncorrectType()

		elif wikiId:
			data["eventSource"] = "PostDetailView"
			url = f"/x{self.comId}/s/item/{wikiId}/vote?cv=1.2"
		else: raise exceptions.IncorrectType()

		response = self.req.make_request(method="POST", endpoint=url, body=dumps(body))
		return response.status_code


	def unlike_blog(self, blogId: str = None, wikiId: str = None) -> int:
		if blogId: url = f"/x{self.comId}/s/blog/{blogId}/vote?eventSource=UserProfileView"
		elif wikiId: url = f"/x{self.comId}/s/item/{wikiId}/vote?eventSource=PostDetailView"
		else: raise exceptions.IncorrectType()

		response = self.req.make_request(method="DELETE", endpoint=url)
		return response.status_code

	def like_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None) -> int:
		data = {
			"value": 1,
			"timestamp": int(timestamp() * 1000)
		}

		if userId:
			data["eventSource"] = "UserProfileView"
			url = f"/x{self.comId}/s/user-profile/{userId}/comment/{commentId}/vote?cv=1.2&value=1"

		elif blogId:
			data["eventSource"] = "PostDetailView"
			url = f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=1"

		elif wikiId:
			data["eventSource"] = "PostDetailView"
			url = f"/x{self.comId}/s/item/{wikiId}/comment/{commentId}/g-vote?cv=1.2&value=1"

		else: raise exceptions.IncorrectType()

		response = self.req.make_request(method="POST", endpoint=url, body=dumps(data))
		return response.status_code


	def unlike_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None) -> int:
		if userId: url = f"/x{self.comId}/s/user-profile/{userId}/comment/{commentId}/g-vote?eventSource=UserProfileView"
		elif blogId: url = f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}/g-vote?eventSource=PostDetailView"
		elif wikiId: url = f"/x{self.comId}/s/item/{wikiId}/comment/{commentId}/g-vote?eventSource=PostDetailView"
		else: raise exceptions.IncorrectType()

		response = self.req.make_request(method="DELETE", endpoint=url)
		return response.status_code

	def upvote_comment(self, blogId: str, commentId: str):
		data = dumps({
			"value": 1,
			"eventSource": "PostDetailView",
			"timestamp": int(timestamp() * 1000)
		})

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=1", body=data)
		return response.status_code


	def downvote_comment(self, blogId: str, commentId: str):
		data = dumps({
			"value": -1,
			"eventSource": "PostDetailView",
			"timestamp": int(timestamp() * 1000)
		})

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=-1", body=data)
		return response.status_code


	def unvote_comment(self, blogId: str, commentId: str):

		response = self.req.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?eventSource=PostDetailView")
		return response.status_code


	def reply_wall(self, userId: str, commentId: str, message: str):
		data = dumps({
			"content": message,
			"stackedId": None,
			"respondTo": commentId,
			"type": 0,
			"eventSource": "UserProfileView",
			"timestamp": int(timestamp() * 1000)
		})

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/user-profile/{userId}/comment", body=data)
		return response.status_code



	def activity_status(self, status: str):
		if "on" in status.lower(): status = 1
		elif "off" in status.lower(): status = 2
		else: raise exceptions.IncorrectType(status)

		data = dumps({
			"onlineStatus": status,
			"duration": 86400,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/user-profile/{self.profile.userId}/online-status", body=data)
		return response.status_code		



	def watch_ad(self):

		response = self.req.make_request(method="POST", endpoint=f"/g/s/wallet/ads/video/start")
		return response.status_code		

	def check_notifications(self):

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/notification/checked")
		return response.status_code	


	def delete_notification(self, notificationId: str):

		response = self.req.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/notification/{notificationId}")
		return response.status_code


	def clear_notifications(self):

		response = self.req.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/notification")
		return response.status_code


	def start_chat(self, userId: Union[str, list], message: str, title: str = None, content: str = None, isGlobal: bool = False, publishToGlobal: bool = False):
		if isinstance(userId, str): userIds = [userId]
		elif isinstance(userId, list): userIds = userId
		else: raise exceptions.IncorrectType(type(userId))

		data = {
			"title": title,
			"inviteeUids": userIds,
			"initialMessageContent": message,
			"content": content,
			"publishToGlobal": 1 if publishToGlobal else 0,
			"timestamp": int(timestamp() * 1000)
		}

		if isGlobal:
			data["type"] = 2
			data["eventSource"] = "GlobalComposeMenu"
		else: data["type"] = 0
		
		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread", body=dumps(data))
		return objects.Thread(response.json()["thread"])

	def invite_to_chat(self, userId: Union[str, list], chatId: str):

		if isinstance(userId, str): userIds = [userId]
		elif isinstance(userId, list): userIds = userId
		else: raise exceptions.IncorrectType(type(userId))

		data = dumps({
			"uids": userIds,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/member/invite", body=data)
		return response.status_code



	def add_to_favorites(self, userId: str):

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/user-group/quick-access/{userId}")
		return response.status_code


	def send_coins(self, coins: int, blogId: str = None, chatId: str = None, objectId: str = None, transactionId: str = None):
		data = {
			"coins": coins,
			"tippingContext": {"transactionId": transactionId if transactionId else str(UUID(hexlify(urandom(16)).decode('ascii')))},
			"timestamp": int(timestamp() * 1000)
		}
		if blogId: url = f"/x{self.comId}/s/blog/{blogId}/tipping"
		elif chatId: url = f"/x{self.comId}/s/chat/thread/{chatId}/tipping"
		elif objectId:
			data["objectId"] = objectId
			data["objectType"] = 2
			url = f"/x{self.comId}/s/tipping"
		else: raise exceptions.IncorrectType()

		response = self.req.make_request(method="POST", endpoint=url, body=dumps(data))
		return response.status_code


	def thank_tip(self, chatId: str, userId: str):

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/tipping/tipped-users/{userId}/thank")
		return response.status_code


	def follow(self, userId: Union[str, list]):

		if isinstance(userId, str):
			response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/user-profile/{userId}/member")
		elif isinstance(userId, list):
			response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/user-profile/{self.profile.userId}/joined", body=dumps({"targetUidList": userId, "timestamp": int(timestamp() * 1000)}))
		else:
			raise exceptions.IncorrectType(type(userId))
		return response.status_code


	def unfollow(self, userId: str):

		response = self.req.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/user-profile/{self.profile.userId}/joined/{userId}")
		return response.status_code


	def block(self, userId: str):

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/block/{userId}")
		return response.status_code


	def unblock(self, userId: str):

		response = self.req.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/block/{userId}")
		return response.status_code


	def visit(self, userId: str):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-profile/{userId}?action=visit")
		return response.status_code

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
		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/{'g-flag' if asGuest else 'flag'}", body=dumps(data))
		return response.status_code



	def full_embed(self, link: str, image: BinaryIO, message: str, chatId: str):
		data = {
			"type": 0,
			"content": message,
			"extensions": {
				"linkSnippetList": [{
					"link": link,
					"mediaType": 100,
					"mediaUploadValue": b64encode(image.read()).decode(),
					"mediaUploadValueContentType": "image/png"
				}]
			},
				"clientRefId": int(timestamp() / 10 % 100000000),
				"timestamp": int(timestamp() * 1000),
				"attachedObject": None
		}

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message", body=dumps(data))
		return response.status_code


	def mark_as_read(self, chatId: str, messageId: str):

		data = dumps({
			"messageId": messageId,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/mark-as-read", body=dumps(data))
		return response.status_code



	def transfer_host(self, chatId: str, userIds: list):
		data = dumps({
			"uidList": userIds,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/transfer-organizer", body=dumps(data))
		return response.status_code


	def accept_host(self, chatId: str, requestId: str):

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept", body=dumps({}))
		return response.status_code


	def kick(self, userId: str, chatId: str, allowRejoin: bool = True):
		if allowRejoin: allowRejoin = 1
		if not allowRejoin: allowRejoin = 0

		response = self.req.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/member/{userId}?allowRejoin={allowRejoin}")
		return response.status_code


		
	def delete_chat(self, chatId: str):

		response = self.req.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}")
		return response.status_code

		
	def subscribe(self, userId: str, autoRenew: str = False, transactionId: str = None):
		if transactionId is None: transactionId = str(UUID(hexlify(urandom(16)).decode('ascii')))

		data = dumps({
			"paymentContext": {
				"transactionId": transactionId,
				"isAutoRenew": autoRenew
			},
			"timestamp": int(timestamp() * 1000)
		})

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/influencer/{userId}/subscribe", body=data)
		return response.status_code


	def promotion(self, noticeId: str, type: str = "accept"):

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/notice/{noticeId}/{type}")
		return response.status_code


	def play_quiz(self, quizId: str, quizAnswerList: list = None, questionIdsList: list = None, answerIdsList: list = None, quizMode: int = 0):

		if quizAnswerList is None:

			if questionIdsList and answerIdsList:
				quizAnswerList = list()

				for question, answer in zip(questionIdsList, answerIdsList):
					part = dumps({
						"optIdList": [answer],
						"quizQuestionId": question,
						"timeSpent": 0.0
					})

					quizAnswerList.append(loads(part))

			else: raise exceptions.IncorrectType()

		data = dumps({
			"mode": quizMode,
			"quizAnswerList": quizAnswerList,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/blog/{quizId}/quiz/result", body=data)
		return response.status_code

	def vc_permission(self, chatId: str, permission: int):

		data = dumps({
			"vvChatJoinType": permission,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/vvchat-permission", body=data)
		return response.status_code


	def get_vc_reputation_info(self, chatId: str):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/avchat-reputation")
		return response.json()


	def claim_vc_reputation(self, chatId: str):

		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/avchat-reputation")
		return response.json()


	def get_all_users(self, type: str = "recent", start: int = 0, size: int = 25):

		if type not in ["recent", "banned", "featured", "leaders", "curators"]:raise exceptions.IncorrectType(type)
		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-profile?type={type}&start={start}&size={size}")
		return objects.userProfileList(response.json())


	def get_online_users(self, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/live-layer?topic=ndtopic:x{self.comId}:online-members&start={start}&size={size}")
		return objects.userProfileList(response.json())


	def get_online_favorite_users(self, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-group/quick-access?type=online&start={start}&size={size}")
		return objects.userProfileList(response.json())


	def get_user_info(self, userId: str):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-profile/{userId}")
		return objects.UserProfile(response.json()["userProfile"])


	def get_user_following(self, userId: str, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-profile/{userId}/joined?start={start}&size={size}")
		return objects.userProfileList(response.json()["userProfileList"])


	def get_user_followers(self, userId: str, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-profile/{userId}/member?start={start}&size={size}")
		return objects.userProfileList(response.json()["userProfileList"])


	def get_user_visitors(self, userId: str, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-profile/{userId}/visitors?start={start}&size={size}")
		return response.json()

	def get_user_checkins(self, userId: str, timezone: int = -timezone // 1000):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/check-in/stats/{userId}?timezone={timezone}")
		return response.json()


	def get_user_blogs(self, userId: str, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/blog?type=user&q={userId}&start={start}&size={size}")
		return response.json()["blogList"]


	def get_user_wikis(self, userId: str, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/item?type=user-all&start={start}&size={size}&cv=1.2&uid={userId}")
		return response.json()["itemList"]


	def get_user_achievements(self, userId: str):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-profile/{userId}/achievements")
		return response.json()["achievements"]

	def get_influencer_fans(self, userId: str, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/influencer/{userId}/fans?start={start}&size={size}")
		return response.json()


	def get_blocked_users(self, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/block?start={start}&size={size}")
		return objects.userProfileList(response.json()["userProfileList"])


	def get_blocker_users(self, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/block?start={start}&size={size}")
		return response.json()["blockerUidList"]

	def search_users(self, nickname: str, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-profile?type=name&q={nickname}&start={start}&size={size}")
		return userProfileList(response.json()["userProfileList"])


	def get_saved_blogs(self, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/bookmark?start={start}&size={size}")
		return response.json()["bookmarkList"]

	"""
	def get_leaderboard_info(self, type: str, start: int = 0, size: int = 25):
		if "24" in type or "hour" in type: response = self.session.get(f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=1&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
		elif "7" in type or "day" in type: response = self.session.get(f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=2&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
		elif "rep" in type: response = self.session.get(f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=3&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
		elif "check" in type: response = self.session.get(f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=4", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
		elif "quiz" in type: response = self.session.get(f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=5&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
		else: raise exceptions.WrongType(type)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return objects.UserProfileList(json.loads(response.text)["userProfileList"]).UserProfileList

	"""


	def get_wiki_info(self, wikiId: str):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/item/{wikiId}")
		return response.json()

	def get_recent_wiki_items(self, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/item?type=catalog-all&start={start}&size={size}")
		return response.json()["itemList"]


	def get_wiki_items(self, categoryId: str = None, start: int = 0, size: int = 100):
		fId = f"/{categoryId}?pagingType=t&size={size}&start={start}" if categoryId else ""

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/item-category{fId}")
		return objects.WikiFoldes(response.json())


	def get_tipped_users(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, chatId: str = None, start: int = 0, size: int = 25):
		if blogId or quizId:url = f"/x{self.comId}/s/blog/{blogId if blogId else quizId}/tipping/tipped-users-summary?start={start}&size={size}"
		elif wikiId: url = f"/x{self.comId}/s/item/{wikiId}/tipping/tipped-users-summary?start={start}&size={size}"
		elif chatId: url = f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/tipping/tipped-users-summary?start={start}&size={size}"
		elif fileId: url = f"/x{self.comId}/s/shared-folder/files/{fileId}/tipping/tipped-users-summary?start={start}&size={size}"
		else: raise exceptions.IncorrectType()

		response = self.req.make_request(method="GET", endpoint=url)
		return response.json()


	def get_my_chats(self, start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/chat/thread?type=joined-me&start={start}&size={size}")
		return objects.ThreadList(response.json()["threadList"])


	def get_public_chats(self, type: str = "recommended", start: int = 0, size: int = 25):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/chat/thread?type=public-all&filterType={type}&start={start}&size={size}")
		return objects.ThreadList(response.json()["threadList"])


	def get_chat_thread(self, chatId: str):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}")
		return objects.Thread(response.json()["thread"])


	def get_chat_messages(self, chatId: str, size: int = 25, pageToken: str = None):

		response = self.req.make_request(method="GET",endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message?v=2&pagingType=t&size={size}{f'&pageToken={pageToken}' if pageToken else ''}")
		return objects.MessageList(response.json())

	def get_message_info(self, chatId: str, messageId: str):

		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}")
		return objects.Message(response.json()["message"])


	def get_blog_info(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None):

		if fileId:
			response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/shared-folder/files/{fileId}")
			return response.json()["file"]


		if blogId or quizId:
			url = f"/x{self.comId}/s/blog/{blogId if blogId else quizId}"
		elif wikiId:
			url = f"/x{self.comId}/s/blog/{wikiId}"
		else:
			raise exceptions.IncorrectType()

		response = self.req.make_request(method="GET", endpoint=url)
		return response.json()


	def get_blog_comments(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, sorting: str = "newest", start: int = 0, size: int = 25):

		if sorting not in ["newest", "vote", "oldest"]: raise exceptions.IncorrectType(sorting)

		if blogId or quizId:
			url = f"/x{self.comId}/s/blog/{blogId if blogId else quizId}/comment?sort={sorting}&start={start}&size={size}"
		elif wikiId:
			url = f"/x{self.comId}/s/item/{wikiId}/comment?sort={sorting}&start={start}&size={size}"
		elif fileId:
			url = f"/x{self.comId}/s/shared-folder/files/{fileId}/comment?sort={sorting}&start={start}&size={size}"
		else:
			raise exceptions.IncorrectType()

		response = self.req.make_request(method="GET", endpoint=url)
		return response.json()["commentList"]




	def get_blog_categories(self, size: int = 25):


		response = self.req.make_request(method="GET", endpoint=f"/x{self.comId}/s/blog-category?size={size}")
		return response.json()["blogCategoryList"]

	def get_blogs_by_category(self, categoryId: str,start: int = 0, size: int = 25):

		response = self.req.make_request(method=f"GET", endpoint=f"/x{self.comId}/s/blog-category/{categoryId}/blog-list?start={start}&size={size}")
		return response.json()["blogList"]


	def get_quiz_rankings(self, quizId: str, start: int = 0, size: int = 25):

		response = self.req.make_request(method=f"GET", endpoint=f"/x{self.comId}/s/blog/{quizId}/quiz/result?start={start}&size={size}")
		return response.json()


	def get_wall_comments(self, userId: str, sorting: str, start: int = 0, size: int = 25):

		if sorting not in ["newest", "vote", "oldest"]: raise exceptions.IncorrectType(sorting)

		response = self.req.make_request(method=f"GET", endpoint=f"/x{self.comId}/s/user-profile/{userId}/comment?sort={sorting}&start={start}&size={size}")
		return response.json()["commentList"]


	def get_recent_blogs(self, pageToken: str = None, start: int = 0, size: int = 25):

		response = self.req.make_request(method=f"GET", endpoint=f"/x{self.comId}/s/feed/blog-all?pagingType=t&{f'pageToken={pageToken}' if pageToken else f'start={start}'}&size={size}")
		return response.json()


	def get_chat_users(self, chatId: str, start: int = 0, size: int = 25):

		response = self.req.make_request(method=f"GET", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/member?start={start}&size={size}&type=default&cv=1.2")
		return objects.userProfileList(response.json()["memberList"])



	def get_notifications(self, start: int = 0, size: int = 25):


		response = self.req.make_request(method=f"GET", endpoint=f"/x{self.comId}/s/notification?pagingType=t&start={start}&size={size}")
		return response.json()["notificationList"]


	def get_notices(self, start: int = 0, size: int = 25):


		response = self.req.make_request(method=f"GET", endpoint=f"/x{self.comId}/s/notice?type=usersV2&status=1&start={start}&size={size}")
		return response.json()["noticeList"]


	def get_sticker_pack_info(self, sticker_pack_id: str):

		response = self.req.make_request(method=f"GET", endpoint=f"/x{self.comId}/s/sticker-collection/{sticker_pack_id}?includeStickers=true")
		return response.json()["stickerCollection"]


	def get_sticker_packs(self):

		response = self.req.make_request(method=f"GET", endpoint=f"/x{self.comId}/s/sticker-collection?includeStickers=false&type=my-active-collection")
		return response.json()["stickerCollection"]



	def get_store_chat_bubbles(self, start: int = 0, size: int = 25):

		response = self.req.make_request(method=f"GET", endpoint=f"/x{self.comId}/s/store/items?sectionGroupId=chat-bubble&start={start}&size={size}")
		return response.json()



	def get_store_stickers(self, start: int = 0, size: int = 25):

		response = self.req.make_request(method=f"GET", endpoint=f"/x{self.comId}/s/store/items?sectionGroupId=sticker&start={start}&size={size}")
		return response.json()



	def get_community_stickers(self):

		response = self.req.make_request(method=f"GET", endpoint=f"/x{self.comId}/s/sticker-collection?type=community-shared")
		return response.json()


	def get_sticker_collection(self, collectionId: str):

		response = self.req.make_request(method=f"GET", endpoint=f"/x{self.comId}/s/sticker-collection/{collectionId}?includeStickers=true")
		return response.json()["stickerCollection"]


	def get_shared_folder_info(self):

		response = self.req.make_request(method=f"GET", endpoint=f"/x{self.comId}/s/shared-folder/stats")
		return response.json()["stats"]


	def get_shared_folder_files(self, type: str = "latest", start: int = 0, size: int = 25):

		response = self.req.make_request(method=f"GET", endpoint=f"/x{self.comId}/s/shared-folder/files?type={type}&start={start}&size={size}")
		return response.json()["fileList"]




	def moderation_history(self, userId: str = None, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, size: int = 25):
		if userId: url = f"/x{self.comId}/s/admin/operation?objectId={userId}&objectType=0&pagingType=t&size={size}"
		elif blogId: url = f"/x{self.comId}/s/admin/operation?objectId={blogId}&objectType=1&pagingType=t&size={size}"
		elif quizId: url = f"/x{self.comId}/s/admin/operation?objectId={quizId}&objectType=1&pagingType=t&size={size}"
		elif wikiId: url = f"/x{self.comId}/s/admin/operation?objectId={wikiId}&objectType=2&pagingType=t&size={size}"
		elif fileId: url = f"/x{self.comId}/s/admin/operation?objectId={fileId}&objectType=109&pagingType=t&size={size}"
		else: url = f"/x{self.comId}/s/admin/operation?pagingType=t&size={size}"

		response = self.req.make_request(method=f"GET", endpoint=url)
		return response.json()["adminLogList"]



	def feature(self, time: int, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None):
		if chatId:
			if time == 1: time = 3600
			if time == 1: time = 7200
			if time == 1: time = 10800

		else:
			if time == 1: time = 86400
			elif time == 2: time = 172800
			elif time == 3: time = 259200
			else: raise exceptions.WrongType(time)

		data = {
			"adminOpName": 114,
			"adminOpValue": {
				"featuredDuration": time
			},
			"timestamp": int(timestamp() * 1000)
		}

		if userId:
			data["adminOpValue"] = {"featuredType": 4}
			data = json.dumps(data)
			response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)

		elif blogId:
			data["adminOpValue"] = {"featuredType": 1}
			data = json.dumps(data)
			response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)

		elif wikiId:
			data["adminOpValue"] = {"featuredType": 1}
			data = json.dumps(data)
			response = self.session.post(f"{self.api}/x{self.comId}/s/item/{wikiId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)

		elif chatId:
			data["adminOpValue"] = {"featuredType": 5}
			data = json.dumps(data)
			response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)

		else: raise exceptions.SpecifyType()
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return json.loads(response.text)

	def unfeature(self, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None):
		data = {
			"adminOpName": 114,
			"adminOpValue": {},
			"timestamp": int(timestamp() * 1000)
		}

		if userId:
			data["adminOpValue"] = {"featuredType": 0}
			data = json.dumps(data)
			response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)

		elif blogId:
			data["adminOpValue"] = {"featuredType": 0}
			data = json.dumps(data)
			response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)

		elif wikiId:
			data["adminOpValue"] = {"featuredType": 0}
			data = json.dumps(data)
			response = self.session.post(f"{self.api}/x{self.comId}/s/item/{wikiId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)

		elif chatId:
			data["adminOpValue"] = {"featuredType": 0}
			data = json.dumps(data)
			response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)

		else: raise exceptions.SpecifyType()
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return json.loads(response.text)

	def hide(self, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, reason: str = None):
		data = {
			"adminOpNote": {
				"content": reason
			},
			"timestamp": int(timestamp() * 1000)
		}

		if userId:
			data["adminOpName"] = 18
			data = json.dumps(data)
			response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)

		elif blogId:
			data["adminOpName"] = 110
			data["adminOpValue"] = 9
			data = json.dumps(data)
			response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)

		elif quizId:
			data["adminOpName"] = 110
			data["adminOpValue"] = 9
			data = json.dumps(data)
			response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{quizId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)

		elif wikiId:
			data["adminOpName"] = 110
			data["adminOpValue"] = 9
			data = json.dumps(data)
			response = self.session.post(f"{self.api}/x{self.comId}/s/item/{wikiId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)

		elif chatId:
			data["adminOpName"] = 110
			data["adminOpValue"] = 9
			data = json.dumps(data)
			response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)

		elif fileId:
			data["adminOpName"] = 110
			data["adminOpValue"] = 9
			data = json.dumps(data)
			response = self.session.post(f"{self.api}/x{self.comId}/s/shared-folder/files/{fileId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)

		else: raise exceptions.SpecifyType()
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return json.loads(response.text)

	def unhide(self, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, reason: str = None):
		data = {
			"adminOpNote": {
				"content": reason
			},
			"timestamp": int(timestamp() * 1000)
		}

		if userId:
			data["adminOpName"] = 19
			data = json.dumps(data)
			response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)

		elif blogId:
			data["adminOpName"] = 110
			data["adminOpValue"] = 0
			data = json.dumps(data)
			response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)

		elif quizId:
			data["adminOpName"] = 110
			data["adminOpValue"] = 0
			data = json.dumps(data)
			response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{quizId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)

		elif wikiId:
			data["adminOpName"] = 110
			data["adminOpValue"] = 0
			data = json.dumps(data)
			response = self.session.post(f"{self.api}/x{self.comId}/s/item/{wikiId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)

		elif chatId:
			data["adminOpName"] = 110
			data["adminOpValue"] = 0
			data = json.dumps(data)
			response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)

		elif fileId:
			data["adminOpName"] = 110
			data["adminOpValue"] = 0
			data = json.dumps(data)
			response = self.session.post(f"{self.api}/x{self.comId}/s/shared-folder/files/{fileId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)

		else: raise exceptions.SpecifyType()
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return json.loads(response.text)

	def edit_titles(self, userId: str, titles: list, colors: list):
		tlt = []
		for titles, colors in zip(titles, colors):
			tlt.append({"title": titles, "color": colors})

		data = json.dumps({
			"adminOpName": 207,
			"adminOpValue": {
				"titles": tlt
			},
			"timestamp": int(timestamp() * 1000)
		})

		response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return json.loads(response.text)

	# TODO : List all warning texts
	def warn(self, userId: str, reason: str = None):
		data = json.dumps({
			"uid": userId,
			"title": "Custom",
			"content": reason,
			"attachedObject": {
				"objectId": userId,
				"objectType": 0
			},
			"penaltyType": 0,
			"adminOpNote": {},
			"noticeType": 7,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.session.post(f"{self.api}/x{self.comId}/s/notice", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return json.loads(response.text)

	# TODO : List all strike texts
	def strike(self, userId: str, time: int, title: str = None, reason: str = None):
		if time == 1: time = 86400
		elif time == 2: time = 10800
		elif time == 3: time = 21600
		elif time == 4: time = 43200
		elif time == 5: time = 86400
		else: raise exceptions.WrongType(time)

		data = json.dumps({
			"uid": userId,
			"title": title,
			"content": reason,
			"attachedObject": {
				"objectId": userId,
				"objectType": 0
			},
			"penaltyType": 1,
			"penaltyValue": time,
			"adminOpNote": {},
			"noticeType": 4,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.session.post(f"{self.api}/x{self.comId}/s/notice", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return json.loads(response.text)

	def ban(self, userId: str, reason: str, banType: int = None):
		data = json.dumps({
			"reasonType": banType,
			"note": {
				"content": reason
			},
			"timestamp": int(timestamp() * 1000)
		})

		response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/ban", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return json.loads(response.text)

	def unban(self, userId: str, reason: str):
		data = json.dumps({
			"note": {
				"content": reason
			},
			"timestamp": int(timestamp() * 1000)
		})

		response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/unban", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return json.loads(response.text)

	def reorder_featured_users(self, userIds: list):
		data = json.dumps({
			"uidList": userIds,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/featured/reorder", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return json.loads(response.text)

	def get_hidden_blogs(self, start: int = 0, size: int = 25):
		response = self.session.get(f"{self.api}/x{self.comId}/s/feed/blog-disabled?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return objects.BlogList(json.loads(response.text)["blogList"]).BlogList

	def get_featured_users(self, start: int = 0, size: int = 25):
		response = self.session.get(f"{self.api}/x{self.comId}/s/user-profile?type=featured&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return objects.UserProfileCountList(json.loads(response.text)).UserProfileCountList

	def review_quiz_questions(self, quizId: str):
		response = self.session.get(f"{self.api}/x{self.comId}/s/blog/{quizId}?action=review", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return objects.QuizQuestionList(json.loads(response.text)["blog"]["quizQuestionList"]).QuizQuestionList

	def get_recent_quiz(self, start: int = 0, size: int = 25):
		response = self.session.get(f"{self.api}/x{self.comId}/s/blog?type=quizzes-recent&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return objects.BlogList(json.loads(response.text)["blogList"]).BlogList

	def get_trending_quiz(self, start: int = 0, size: int = 25):
		response = self.session.get(f"{self.api}/x{self.comId}/s/feed/quiz-trending?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return objects.BlogList(json.loads(response.text)["blogList"]).BlogList

	def get_best_quiz(self, start: int = 0, size: int = 25):
		response = self.session.get(f"{self.api}/x{self.comId}/s/feed/quiz-best-quizzes?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return objects.BlogList(json.loads(response.text)["blogList"]).BlogList

	def send_action(self, actions: list, blogId: str = None, quizId: str = None, lastAction: bool = False):
		# Action List
		# Browsing

		if lastAction is True: t = 306
		else: t = 304

		data = {
			"o": {
				"actions": actions,
				"target": f"ndc://x{self.comId}/",
				"ndcId": int(self.comId),
				"params": {"topicIds": [45841, 17254, 26542, 42031, 22542, 16371, 6059, 41542, 15852]},
				"id": "831046"
			},
			"t": t
		}

		if blogId is not None or quizId is not None:
			data["target"] = f"ndc://x{self.comId}/blog/{blogId}"
			if blogId is not None: data["params"]["blogType"] = 0
			if quizId is not None: data["params"]["blogType"] = 6

		return self.send(json.dumps(data))

	# Provided by "spectrum#4691"
	def purchase(self, objectId: str, objectType: int, aminoPlus: bool = True, autoRenew: bool = False):
		data = {'objectId': objectId,
				'objectType': objectType,
				'v': 1,
				"timestamp": int(timestamp() * 1000)}

		if aminoPlus: data['paymentContext'] = {'discountStatus': 1, 'discountValue': 1, 'isAutoRenew': autoRenew}
		else: data['paymentContext'] = {'discountStatus': 0, 'discountValue': 1, 'isAutoRenew': autoRenew}

		data = json.dumps(data)
		response = self.session.post(f"{self.api}/x{self.comId}/s/store/purchase", headers=self.parse_headers(data=data), data=data)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return response.status_code

	# Provided by "spectrum#4691"
	def apply_avatar_frame(self, avatarId: str, applyToAll: bool = True):
		"""
		Apply avatar frame.

		**Parameters**
			- **avatarId** : ID of the avatar frame.
			- **applyToAll** : Apply to all.

		**Returns**
			- **Success** : 200 (int)

			- **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`

		"""

		data = {"frameId": avatarId,
				"applyToAll": 0,
				"timestamp": int(timestamp() * 1000)}

		if applyToAll: data["applyToAll"] = 1

		data = json.dumps(data)
		response = self.session.post(f"{self.api}/x{self.comId}/s/avatar-frame/apply", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return response.status_code

	def invite_to_vc(self, chatId: str, userId: str):
		"""
		Invite a User to a Voice Chat

		**Parameters**
			- **chatId** - ID of the Chat
			- **userId** - ID of the User

		**Returns**
			- **Success** : 200 (int)

			- **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
		"""

		data = json.dumps({
			"uid": userId
		})

		response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/vvchat-presenter/invite/", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return response.status_code

	def add_poll_option(self, blogId: str, question: str):
		data = json.dumps({
			"mediaList": None,
			"title": question,
			"type": 0,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/poll/option", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return response.status_code

	def create_wiki_category(self, title: str, parentCategoryId: str, content: str = None):
		data = json.dumps({
			"content": content,
			"icon": None,
			"label": title,
			"mediaList": None,
			"parentCategoryId": parentCategoryId,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.session.post(f"{self.api}/x{self.comId}/s/item-category", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return response.status_code

	def create_shared_folder(self,title: str):
		data = json.dumps({
				"title":title,
				"timestamp":int(timestamp() * 1000)
			})
		response = self.session.post(f"{self.api}/x{self.comId}/s/shared-folder/folders", headers=self.parse_headers(data=data),data=data, proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return response.status_code

	def submit_to_wiki(self, wikiId: str, message: str):
		data = json.dumps({
			"message": message,
			"itemId": wikiId,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.session.post(f"{self.api}/x{self.comId}/s/knowledge-base-request", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return response.status_code

	def accept_wiki_request(self, requestId: str, destinationCategoryIdList: list):
		data = json.dumps({
			"destinationCategoryIdList": destinationCategoryIdList,
			"actionType": "create",
			"timestamp": int(timestamp() * 1000)
		})

		response = self.session.post(f"{self.api}/x{self.comId}/s/knowledge-base-request/{requestId}/approve", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return response.status_code

	def reject_wiki_request(self, requestId: str):
		data = json.dumps({})

		response = self.session.post(f"{self.api}/x{self.comId}/s/knowledge-base-request/{requestId}/reject", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return response.status_code

	def get_wiki_submissions(self, start: int = 0, size: int = 25):
		response = self.session.get(f"{self.api}/x{self.comId}/s/knowledge-base-request?type=all&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return objects.WikiRequestList(json.loads(response.text)["knowledgeBaseRequestList"]).WikiRequestList

	def get_live_layer(self):
		response = self.session.get(f"{self.api}/x{self.comId}/s/live-layer/homepage?v=2", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return objects.LiveLayer(json.loads(response.text)["liveLayerList"]).LiveLayer

	def apply_bubble(self, bubbleId: str, chatId: str, applyToAll: bool = False):
		data = {
			"applyToAll": 0,
			"bubbleId": bubbleId,
			"threadId": chatId,
			"timestamp": int(timestamp() * 1000)
		}

		if applyToAll is True:
			data["applyToAll"] = 1

		data = json.dumps(data)
		response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/apply-bubble", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
		if response.status_code != 200: 
			return exceptions.CheckException(response.text)
		else: return response.status_code
