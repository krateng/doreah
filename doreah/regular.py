from threading import Thread, Timer

from ._internal import DEFAULT, defaultarguments, gopen, doreahconfig


_config = {}

_yearly_funcs = []
_monthly_funcs = []
_daily_funcs = []

# set configuration
def config():
	"""Configures default values for this module.

	These defaults define behaviour of function calls when respective arguments are omitted. Any call of this function will overload the configuration in the .doreah file of the project. This function must be called with all configurations, as any omitted argument will reset to default, even if it has been changed with a previous function call."""
	global _config

# initial config on import, set everything to default
config()


def startpulse():
	# execute all actions for startup
	# they will themselves trigger their next pass
	execute_yearly()
	execute_monthly()
	execute_daily()

def execute_yearly():
	# schedule for next year
	now = datetime.datetime.utcnow()
	nextyear = datetime.datetime(now.year+1,1,1)
	wait = nextyear.timestamp() - now.timestamp() + 5
	Timer(wait,execute_yearly).start()

	for func in _yearly_funcs:
		func()
def execute_monthly():
	# schedule for next month
	now = datetime.datetime.utcnow()
	nextmonth = datetime.datetime(now.year,now.month + 1,1) if now.month != 12 else datetime.datetime(now.year+1,1,1)
	wait = nextmonth.timestamp() - now.timestamp() + 5
	Timer(wait,execute_monthly).start()

	for func in _monthly_funcs:
		func()
def execute_daily():
	# schedule for tomorrow
	now = datetime.datetime.utcnow()
	nextday = datetime.datetime(now.year,now.month,now.day) + datetime.timedelta(days=1)
	wait = nextday.timestamp() - now.timestamp() + 5
	Timer(wait,execute_daily).start()

	for func in _daily_funcs:
		func()

def yearly(func):

	_yearly_funcs.append(func)
	return func
def monthly(func):

	_monthly_funcs.append(func)
	return func

def daily(func):

	_daily_funcs.append(func)
	return func
