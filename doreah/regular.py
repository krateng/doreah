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
	"""Decorator for yearly functions. Depending on configuration, is equivalent to either :meth:`runyearly` or :meth:`repeatyearly`."""
	if _config["autostart"]: return runyearly(func)
	else: return repeatyearly(func)

def monthly(func):
	"""Decorator for monthly functions. Depending on configuration, is equivalent to either :meth:`runmonthly` or :meth:`repeatmonthly`."""
	if _config["autostart"]: return runmonthly(func)
	else: return repeatmonthly(func)

def daily(func):
	"""Decorator for daily functions. Depending on configuration, is equivalent to either :meth:`rundaily` or :meth:`repeatdaily`."""
	if _config["autostart"]: return rundaily(func)
	else: return repeatdaily(func)

def hourly(func):
	"""Decorator for hourly functions. Depending on configuration, is equivalent to either :meth:`runhourly` or :meth:`repeathourly`."""
	if _config["autostart"]: return runhourly(func)
	else: return repeathourly(func)




def runyearly(func):
	"""Decorator to make the function execute on first definition as well as every year."""

	def self_scheduling_func():
		# execute function
		func()

		# schedule next execution
		now = datetime.datetime.utcnow()
		nextyear = datetime.datetime(now.year+1,1,1)
		wait = nextyear.timestamp() - now.timestamp() + 5
		Timer(wait,self_scheduling_func).start()

	# now execute it for the first time
	t = Timer(5,self_scheduling_func)
	t.daemon = True
	t.start()
	return func


def repeatyearly(func):
	"""Decorator to make the function repeat every new year after being called once."""

	def self_scheduling_func(*args,**kwargs):
		# execute function
		func(*args,**kwargs)

		# schedule next execution
		now = datetime.datetime.utcnow()
		nextyear = datetime.datetime(now.year+1,1,1)
		wait = nextyear.timestamp() - now.timestamp() + 5
		Timer(wait,self_scheduling_func,args=args,kwargs=kwargs).start()

	def starter(*args,**kwargs):
		t = Thread(target=self_scheduling_func,args=args,kwargs=kwargs)
		t.daemon = True
		t.start()
	return starter

def runmonthly(func):
	"""Decorator to make the function execute on first definition as well as every month."""

	def self_scheduling_func():
		# execute function
		func()

		# schedule next execution
		now = datetime.datetime.utcnow()
		nextmonth = datetime.datetime(now.year,now.month + 1,1) if now.month != 12 else datetime.datetime(now.year+1,1,1)
		wait = nextmonth.timestamp() - now.timestamp() + 5
		Timer(wait,self_scheduling_func).start()

	# now execute it for the first time
	t = Timer(5,self_scheduling_func)
	t.daemon = True
	t.start()
	return func


def repeatmonthly(func):
	"""Decorator to make the function repeat every new month after being called once."""

	def self_scheduling_func(*args,**kwargs):
		# execute function
		func(*args,**kwargs)

		# schedule next execution
		now = datetime.datetime.utcnow()
		nextmonth = datetime.datetime(now.year,now.month + 1,1) if now.month != 12 else datetime.datetime(now.year+1,1,1)
		wait = nextmonth.timestamp() - now.timestamp() + 5
		Timer(wait,self_scheduling_func,args=args,kwargs=kwargs).start()

	def starter(*args,**kwargs):
		t = Thread(target=self_scheduling_func,args=args,kwargs=kwargs)
		t.daemon = True
		t.start()
	return starter

def rundaily(func):
	"""Decorator to make the function execute on first definition as well as every day."""

	def self_scheduling_func():
		# execute function
		func()

		# schedule next execution
		now = datetime.datetime.utcnow()
		nextday = datetime.datetime(now.year,now.month,now.day) + datetime.timedelta(days=1)
		wait = nextday.timestamp() - now.timestamp() + 5
		Timer(wait,self_scheduling_func).start()

	# now execute it for the first time
	t = Timer(5,self_scheduling_func)
	t.daemon = True
	t.start()
	return func


def repeatdaily(func):
	"""Decorator to make the function repeat every new day after being called once."""

	def self_scheduling_func(*args,**kwargs):
		# execute function
		func(*args,**kwargs)

		# schedule next execution
		now = datetime.datetime.utcnow()
		nextday = datetime.datetime(now.year,now.month,now.day) + datetime.timedelta(days=1)
		wait = nextday.timestamp() - now.timestamp() + 5
		Timer(wait,self_scheduling_func,args=args,kwargs=kwargs).start()

	def starter(*args,**kwargs):
		t = Thread(target=self_scheduling_func,args=args,kwargs=kwargs)
		t.daemon = True
		t.start()
	return starter



def runhourly(func):
	"""Decorator to make the function execute on first definition as well as every hour."""

	def self_scheduling_func():
		# execute function
		func()

		# schedule next execution
		now = datetime.datetime.utcnow()
		nexthour = datetime.datetime(now.year,now.month,now.day,now.hour) + datetime.timedelta(hours=1)
		wait = nexthour.timestamp() - now.timestamp() + 5
		Timer(wait,self_scheduling_func).start()

	# now execute it for the first time
	t = Timer(5,self_scheduling_func)
	t.daemon = True
	t.start()
	return func


def repeathourly(func):
	"""Decorator to make the function repeat every new hour after being called once."""

	def self_scheduling_func(*args,**kwargs):
		# execute function
		func(*args,**kwargs)

		# schedule next execution
		now = datetime.datetime.utcnow()
		nexthour = datetime.datetime(now.year,now.month,now.day,now.hour) + datetime.timedelta(hours=1)
		wait = nexthour.timestamp() - now.timestamp() + 5
		Timer(wait,self_scheduling_func,args=args,kwargs=kwargs).start()

	def starter(*args,**kwargs):
		t = Thread(target=self_scheduling_func,args=args,kwargs=kwargs)
		t.daemon = True
		t.start()
	return starter





#for testing
def _runoften(func):
	def self_scheduling_func():
		# execute function
		func()

		# schedule next execution
		wait = 15
		Timer(wait,self_scheduling_func).start()


	# now execute it for the first time

	t = Timer(5,self_scheduling_func)
	t.daemon = True
	t.start()
	return func


def _repeatoften(func):
	def self_scheduling_func(*args,**kwargs):
		# execute function
		func(*args,**kwargs)

		# schedule next execution
		wait = 15
		Timer(wait,self_scheduling_func,args=args,kwargs=kwargs).start()

	def starter(*args,**kwargs):
		t = Thread(target=self_scheduling_func,args=args,kwargs=kwargs)
		t.daemon = True
		t.start()
	return starter


# now check local configuration file
_config.update(doreahconfig("regular"))
