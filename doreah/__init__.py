name = "doreah"
version = 0,11,2
versionstr = ".".join(str(n) for n in version)
author = {
	"name": "Johannes Krattenmacher",
	"email": "python@krateng.dev",
	"github": "krateng"
}
requires = [
	"lxml",
	"mechanicalsoup",
	"requests"
]


__all__ = [
	"caching",
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
