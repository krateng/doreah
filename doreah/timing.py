import time

from ._internal import defaultarguments, doreahconfig

_config = {}

_lastcalls = {}

# set configuration
# si		0 means seconds, 1 ms, 2 μs, 3 ns etc
def config(si=0):
	"""Configures default values for this module.

	These defaults define behaviour of function calls when respective arguments are omitted. Any call of this function will overload the configuration in the .doreah file of the project. This function must be called with all configurations, as any omitted argument will reset to default, even if it has been changed with a previous function call."""
	global _config
	_config["si"] = si


# initial config on import, set everything to default
config()


# Take clock. Returns time passed since last call of this function. if called with an identifier, will only
# consider calls with that identifier. No identifier means any call is valid.
# identifiers	arbitrary strings to remember different timers. guaranteed to set all timers to exactly the same time for
#				all identifiers in one call. will return tuple of all identifiers, singular value if only one identifier
def clock(*identifiers):
	"""Takes the time. Returns elapsed time since last call with that identifier for each identifier,
	or time since last call with any identifier if no identifier is given.

	:param string identifiers: Unique identifiers for timing to be taken
	:return: Tuple of elapsed times for each identifier, or single value if only one identifier or no identifier."""

	global _lastcalls

	if len(identifiers) == 0: identifiers = (None,)

	now = time.time()
	# get last calls
	stamps = (_lastcalls.get(i) for i in identifiers)
	results = tuple(None if lc is None else (now - lc) * (1000**_config["si"]) for lc in stamps)
	if len(results) == 1: results = results[0]

	# set new stamps
	for i in identifiers:
		_lastcalls[i] = now
	_lastcalls[None] = now			# always save last overall call so we can directly access it

	return results



def clockp(name,*identifiers):
	"""Prints out elapsed time since last call according to the rules of :meth:`clock`

	:param string name: Name to be printed out
	:param string identifiers: Unique identifiers for timing to be taken"""
	time = clock(*identifiers)
	print(name + ": " + str(time))






# now check local configuration file
_config.update(doreahconfig("timing"))
