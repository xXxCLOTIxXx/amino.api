
class profile:
	def __init__(self, data: dict = {}):
		self.json = data
		self.sid = self.json.get("sid")
		self.userId = self.json.get("auid")
		self.secret = self.json.get("secret")
		self.account = Account(self.json.get("account", {}))
		self.userProfile = UserProfile(self.json.get("userProfile", {}))


class Account:
	def __init__(self, data: dict = {}):
		self.json = data
		self.username = self.json.get("username")
		self.status = self.json.get("status")
		self.userId = self.json.get("uid")
		self.modifiedTime = self.json.get("modifiedTime")
		self.twitterID = self.json.get("twitterID")
		self.activation = self.json.get("activation")
		self.phoneNumberActivation = self.json.get("phoneNumberActivation")
		self.emailActivation = self.json.get("emailActivation")
		self.appleID = self.json.get("appleID")
		self.nickname = self.json.get("nickname")
		self.mediaList = self.json.get("mediaList")
		self.googleID = self.json.get("googleID")
		self.icon = self.json.get("icon")
		self.securityLevel = self.json.get("securityLevel")
		self.phoneNumber = self.json.get("phoneNumber")
		self.membership = self.json.get("membership")
		self.advancedSettings = self.json.get("advancedSettings")
		self.role = self.json.get("role")
		self.aminoIdEditable = self.json.get("aminoIdEditable")
		self.aminoId = self.json.get("aminoId")
		self.createdTime = self.json.get("createdTime")
		self.extensions = self.json.get("extensions")
		self.email = self.json.get("email")

class UserProfile:
	def __init__(self, data: dict = {}):
		self.json = data
		self.status = self.json.get("status")
		self.moodSticker = self.json.get("moodSticker")
		self.itemsCount = self.json.get("itemsCount")
		self.consecutiveCheckInDays = self.json.get("consecutiveCheckInDays")
		self.userId = self.json.get("uid")
		self.modifiedTime = self.json.get("modifiedTime")
		self.followingStatus = self.json.get("followingStatus")
		self.onlineStatus = self.json.get("onlineStatus")
		self.accountMembershipStatus = self.json.get("accountMembershipStatus")
		self.isGlobal = self.json.get("isGlobal")
		self.reputation = self.json.get("reputation")
		self.postsCount = self.json.get("postsCount")
		self.membersCount = self.json.get("membersCount")
		self.nickname = self.json.get("nickname")
		self.mediaList = self.json.get("mediaList")
		self.icon = self.json.get("icon")
		self.isNicknameVerified = self.json.get("isNicknameVerified")
		self.mood = self.json.get("mood")
		self.level = self.json.get("level")
		self.notificationSubscriptionStatus = self.json.get("notificationSubscriptionStatus")
		self.pushEnabled = self.json.get("pushEnabled")
		self.membershipStatus = self.json.get("membershipStatus")
		self.content = self.json.get("content")
		self.joinedCount = self.json.get("joinedCount")
		self.role = self.json.get("role")
		self.commentsCount = self.json.get("commentsCount")
		self.aminoId = self.json.get("aminoId")
		self.comId = self.json.get("ndcId")
		self.createdTime = self.json.get("createdTime")
		self.extensions = self.json.get("extensions")
		self.storiesCount = self.json.get("storiesCount")
		self.blogsCount = self.json.get("blogsCount")


class linkInfo:
	def __init__(self, data: dict = {}):
		self.json = data
		linkInfo = self.json.get("extensions", {}).get("linkInfo", {})

		self.path = self.json.get("path")
		self.objectId = linkInfo.get("objectId")
		self.targetCode = linkInfo.get("targetCode")
		self.comId = linkInfo.get("ndcId")
		self.fullPath = linkInfo.get("fullPath")
		self.shortCode = linkInfo.get("shortCode")
		self.objectType = linkInfo.get("objectType")


class Event:
	def __init__(self, data: dict = {}):
		self.json = data