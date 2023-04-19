from setuptools import setup, find_packages
from json import load

with open("config.json", "r") as file:
	info = load(file)
if info.get("long_description"):
	long_description=info.get("long_description")
else:
	with open("README.md", "r") as file:
		long_description = file.read()

setup(
	name = info.get("name"),
	version = info.get("version"),
	url = info.get("github_page"),
	download_url = info.get("download_link"),
	license = info.get("license"),
	author = info.get("author"),
	author_email = info.get("author_email"),
	description = info.get("description"),
	long_description = long_description,
	long_description_content_type = info.get("long_description_content_type"),
	keywords = info.get("keywords"),
	install_requires = info.get("install_requires"),
	packages = find_packages()
)
