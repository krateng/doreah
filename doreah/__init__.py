
__all__ = [
	"auth",
	"control",
	"database",
	"datatypes",
	"filesystem",
	"fs",
	"io",
	"logging",
	"packageutils",
	"persistence",
	"regular",
	"settings",
	"timing"

]

from ._internal import config


# useful things for everyone


def deprecated(func):
	"""Function decorator to deprecate a function"""

	def newfunc(*args,**kwargs):
		print("\033[93m" + "Function " + func.__name__ + " is deprecated!" + "\033[0m")
		return func(*args,**kwargs)

	return newfunc
