from json.decoder import JSONDecodeError
from json import loads

class UnknownError(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class InvalidSessionType(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class InvalidFunctionСall(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class SocketNotStarted(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)


class IncorrectType(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class AgeTooLow(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)


class UnsupportedLanguage(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class UnsupportedService(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class InvalidRequest(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class InvalidSession(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class AccessDenied(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class UnexistentData(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class ActionNotAllowed(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class ServiceUnderMaintenance(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class MessageNeeded(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class InvalidAccountOrPassword(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class AccountDisabled(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class InvalidEmail(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class InvalidPassword(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class EmailAlreadyTaken(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class UnsupportedEmail(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class AccountDoesntExist(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class InvalidDevice(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class AccountLimitReached(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class TooManyRequests(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class CantFollowYourself(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class UserUnavailable(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class YouAreBanned(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class UserNotMemberOfCommunity(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class RequestRejected(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class ActivateAccount(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class CantLeaveCommunity(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class ReachedTitleLength(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class EmailFlaggedAsSpam(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class AccountDeleted(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class API_ERR_EMAIL_NO_PASSWORD(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class API_ERR_COMMUNITY_USER_CREATED_COMMUNITIES_VERIFY(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class VerificationRequired(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class API_ERR_INVALID_AUTH_NEW_DEVICE_LINK(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class CommandCooldown(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class UserBannedByTeamAmino(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class IpTemporaryBan(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class InvitesDisabled(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class InvalidLink(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class UnknownError(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class ChatsLimit(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class CommunityNeeded(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class NotAuthorized(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)


class CapchaNotRecognize(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)


class WrongType(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class InternalServerError(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)

class InvalidVerificationCode(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)


class OnlyViewMode(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)



errors = {
	100: UnsupportedService,
	101: InternalServerError,
	103: InvalidRequest,
	104: InvalidRequest,
	105: InvalidSession,
	106: AccessDenied,
	107: UnexistentData,
	110: ActionNotAllowed,
	111: ServiceUnderMaintenance,
	113: MessageNeeded,
	201: AccountDisabled,
	210: AccountDisabled,
	213: InvalidEmail,
	214: InvalidPassword,
	215: UnsupportedEmail,
	216: AccountDoesntExist,
	218: InvalidDevice,
	219: TooManyRequests,
	225: UserUnavailable,
	229: YouAreBanned,
	230: UserNotMemberOfCommunity,
	235: RequestRejected,
	238: ActivateAccount,
	239: CantLeaveCommunity,
	241: EmailFlaggedAsSpam,
	246: AccountDeleted,
	251: API_ERR_EMAIL_NO_PASSWORD,
	257: API_ERR_COMMUNITY_USER_CREATED_COMMUNITIES_VERIFY,
	270: VerificationRequired,
	271: API_ERR_INVALID_AUTH_NEW_DEVICE_LINK,
	291: CommandCooldown,
	293: UserBannedByTeamAmino,
	403: IpTemporaryBan,
	802: InvalidLink,
	1611: InvitesDisabled,
	1602: ChatsLimit,
	1663: OnlyViewMode,
	3102: InvalidVerificationCode

}

def check_exceptions(data):
	try:
		data = loads(data)
		try:code = data["api:statuscode"]
		except:raise UnknownError(data)
	except JSONDecodeError:code = 403
	if code in errors:raise errors[code](data)
	else:raise UnknownError(data)