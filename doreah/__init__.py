name = "doreah"
version = 0,6,3


__all__ = [
	"caching",
	"logging",
	"persistence",
	"settings",
	"timing",
	"tsv"

]




# useful things for everyone


def deprecated(func):
	"""Function decorator to deprecate a function"""

	def newfunc(*args,**kwargs):
		print("\033[93m" + "Function " + func.__name__ + " is deprecated!" + "\033[0m")
		func(*args,**kwargs)

	return newfunc
