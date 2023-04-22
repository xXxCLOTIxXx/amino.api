from typing import Union
from aiohttp import ClientSession
from requests import Session

from .helpers import Generator
from .exceptions import InvalidFunctionСall, InvalidSessionType
from .exceptions import check_exceptions

class Requester:
	def __init__(self, session: Union[ClientSession, Session], deviceId: str = None, auto_device: bool = False, proxies: dict = None, verify = None):
		self.api = "https://service.narvii.com/api/v1"
		self.sid = None
		self.deviceId = deviceId
		self.gen = Generator(auto_device)
		self.session = session
		self.proxies = proxies
		self.verify = verify

		if isinstance(self.session, ClientSession):self.session_type = "async"
		elif isinstance(self.session, Session):self.session_type = "sync"
		else:raise InvalidSessionType(type(self.session))

	def _set(self, act: int, sid: str = None, deviceId: str = None):
		if act == 1:self.sid=sid
		if act == 2:self.deviceId=deviceId


	def make_request(self, method: str, endpoint: str, body = None, type=None, successfully: int = 200, headers = None, files = None, payload = None):
		if self.session_type!="sync":raise InvalidFunctionСall("You cannot select this function, your session type is async")
		
		if payload != None and body == None: type = "==PAYLOAD=="

		response = self.session.request(method, f"{self.api}{endpoint}", files=files, proxies=self.proxies, verify=self.verify, data=body, headers=headers if headers else self.gen.get_headers(sid=self.sid, data=body or payload, deviceId=self.deviceId, content_type=type))
		return check_exceptions(response.text) if response.status_code != successfully else response


	async def make_async_request(self, method: str, endpoint: str, body = None, type=None, successfully: int = 200, headers = None, files = None, payload = None):
		if self.session_type=="sync":raise InvalidFunctionСall("You cannot select this function, your session type is sync")
		
		response = await self.session.request(method, f"{self.api}{endpoint}", files=files, data=body, headers=headers if headers else self.gen.get_headers(sid=self.sid, data=body or payload, deviceId=self.deviceId, content_type=type))
		return check_exceptions(await response.text()) if response.status != successfully else response