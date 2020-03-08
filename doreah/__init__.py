
__all__ = [
	"auth",
	"caching",
	"control",
	"database",
	"datatypes",
	"filesystem",
	"io",
	"logging",
	"packageutils",
	"persistence",
	"pyhp",
	"regular",
	"scraping"
	"settings",
	"timing",
	"tsv"

]

from ._internal import config

from .__pkginfo__ import version




# useful things for everyone


def deprecated(func):
	"""Function decorator to deprecate a function"""

	def newfunc(*args,**kwargs):
		print("\033[93m" + "Function " + func.__name__ + " is deprecated!" + "\033[0m")
		return func(*args,**kwargs)

	return newfunc
