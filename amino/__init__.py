"""
Author: Xsarz

Enjoy using!
"""



from .utils import helpers, exceptions, objects, requester
from .client import Client
from .local_client import LocalClient
from .full_client import FullClient

from .asynclib.client import AsyncClient
from .asynclib.local_client import AsyncLocalClient
from .asynclib.socket import AsyncSocket

from os import system as s
from json import loads
from requests import get

__title__ = 'amino.api'
__author__ = 'Xsarz'
__license__ = 'MIT'
__copyright__ = 'Copyright 2023 Xsarz'
__version__ = '1.1'
__newest__ = loads(get("https://pypi.org/pypi/amino.api/json").text)["info"]["version"]



if __version__ != __newest__:
	s('cls || clear')
	print(f'\033[38;5;214m{__title__} made by {__author__}\nPlease update the library. Your version: {__version__}  A new version:{__newest__}\033[0m')