name = "doreah"
version = 1,2,4
versionstr = ".".join(str(n) for n in version)
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




# useful things for everyone


def deprecated(func):
	"""Function decorator to deprecate a function"""

	def newfunc(*args,**kwargs):
		print("\033[93m" + "Function " + func.__name__ + " is deprecated!" + "\033[0m")
		return func(*args,**kwargs)

	return newfunc
