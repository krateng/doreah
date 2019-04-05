from threading import Thread, Timer
import datetime

from ._internal import DEFAULT, defaultarguments, gopen, doreahconfig


_config = {}

_yearly_funcs = []
_monthly_funcs = []
_daily_funcs = []

# set configuration
def config(autostart=True):
	"""Configures default values for this module.

	These defaults define behaviour of function calls when respective arguments are omitted. Any call of this function will overload the configuration in the .doreah file of the project. This function must be called with all configurations, as any omitted argument will reset to default, even if it has been changed with a previous function call."""
	global _config
	_config["autostart"] = autostart

# initial config on import, set everything to default
config()



def yearly(func):
	"""Decorator to make the function repeat execution every year."""

	def self_scheduling_func():
		# execute function
		func()

		# schedule next execution
		now = datetime.datetime.utcnow()
		nextyear = datetime.datetime(now.year+1,1,1)
		wait = nextyear.timestamp() - now.timestamp() + 5
		Timer(wait,self_scheduling_func).start()

	# now execute it for the first time
	if _config["autostart"]:
		t = Timer(5,self_scheduling_func)
		t.daemon = True
		t.start()
		return self_scheduling_func

	# if we call it manually, we need to make sure the first call creates a new thread
	else:
		def starter():
			t = Thread(target=self_scheduling_func)
			t.daemon = True
			t.start()
		return starter

def monthly(func):
	"""Decorator to make the function repeat execution every month."""

	def self_scheduling_func():
		# execute function
		func()

		# schedule next execution
		now = datetime.datetime.utcnow()
		nextmonth = datetime.datetime(now.year,now.month + 1,1) if now.month != 12 else datetime.datetime(now.year+1,1,1)
		wait = nextmonth.timestamp() - now.timestamp() + 5
		Timer(wait,self_scheduling_func).start()

	# now execute it for the first time
	if _config["autostart"]:
		t = Timer(5,self_scheduling_func)
		t.daemon = True
		t.start()
		return self_scheduling_func

	# if we call it manually, we need to make sure the first call creates a new thread
	else:
		def starter():
			t = Thread(target=self_scheduling_func)
			t.daemon = True
			t.start()
		return starter

def daily(func):
	"""Decorator to make the function repeat execution every day."""

	def self_scheduling_func():
		# execute function
		func()

		# schedule next execution
		now = datetime.datetime.utcnow()
		nextday = datetime.datetime(now.year,now.month,now.day) + datetime.timedelta(days=1)
		wait = nextday.timestamp() - now.timestamp() + 5
		Timer(wait,self_scheduling_func).start()

	# now execute it for the first time
	if _config["autostart"]:
		t = Timer(5,self_scheduling_func)
		t.daemon = True
		t.start()
		return self_scheduling_func

	# if we call it manually, we need to make sure the first call creates a new thread
	else:
		def starter():
			t = Thread(target=self_scheduling_func)
			t.daemon = True
			t.start()
		return starter

#for testing
def _often(func):

	def self_scheduling_func():
		# execute function
		func()

		# schedule next execution
		wait = 5
		Timer(wait,self_scheduling_func).start()

	# now execute it for the first time
	if _config["autostart"]:
		t = Timer(5,self_scheduling_func)
		t.daemon = True
		t.start()
		return self_scheduling_func

	# if we call it manually, we need to make sure the first call creates a new thread
	else:
		def starter():
			t = Thread(target=self_scheduling_func)
			t.daemon = True
			t.start()
		return starter



# now check local configuration file
_config.update(doreahconfig("regular"))
