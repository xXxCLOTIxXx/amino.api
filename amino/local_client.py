from .utils.requester import Requester
from .utils.helpers import Generator
from .utils import objects
from .client import Client

from time import time as timestamp
from json import loads, dumps
from requests import Session


class LocalClient(Client):
	def __init__(self, comId: int, profile: objects.profile, deviceId: str = None, proxies: dict = None, certificatePath = None):
		self.profile = profile
		self.comId = comId
		Client.__init__(self, deviceId=deviceId, proxies=proxies, certificatePath=certificatePath)

	def join_chat(self, chatId: str):
		response = self.req.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}", type="application/x-www-form-urlencoded", proxies=self.proxies, verify=self.certificatePath)
		return response.status_code

	def leave_chat(self, chatId: str):
		response = self.req.make_request(method="DELETE", endpoint=f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}", proxies=self.proxies, verify=self.certificatePath)
		return response.status_code