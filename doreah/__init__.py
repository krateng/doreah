name = "doreah"
version = 1,5,1
versionstr = ".".join(str(n) for n in version)
desc = "Small toolkit of utilities for python projects"
author = {
	"name": "Johannes Krattenmacher",
	"email": "python@krateng.dev",
	"github": "krateng"
}
requires = [
	"lxml",
	"mechanicalsoup",
	"requests",
	"pyyaml",
	"beautifulsoup4"
]
resources = [
	'res/login.pyhp'
]

commands = {
	"pyhpserver":"pyhp2:run_testserver"
}


__all__ = [
	"auth",
	"caching",
	"database",
	"io",
	"logging",
	"persistence",
	"pyhp",
	"regular",
	"scraping"
	"settings",
	"timing",
	"tsv"

]

from ._internal import config




# useful things for everyone


def deprecated(func):
	"""Function decorator to deprecate a function"""

	def newfunc(*args,**kwargs):
		print("\033[93m" + "Function " + func.__name__ + " is deprecated!" + "\033[0m")
		return func(*args,**kwargs)

	return newfunc
