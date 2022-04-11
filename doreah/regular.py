from threading import Thread, Timer
import datetime
import random
import time

from ._internal import DEFAULT, defaultarguments, gopen, DoreahConfig


config = DoreahConfig("regular",
	autostart=True,
	offset=0
)

def tz():
	return datetime.timezone(offset=datetime.timedelta(hours=config["offset"]))

### DEPRECATED
def yearly(func):
	"""Decorator for yearly functions. Depending on configuration, is equivalent to either :meth:`runyearly` or :meth:`repeatyearly`."""
	if config["autostart"]: return runyearly(func)
	else: return repeatyearly(func)

def monthly(func):
	"""Decorator for monthly functions. Depending on configuration, is equivalent to either :meth:`runmonthly` or :meth:`repeatmonthly`."""
	if config["autostart"]: return runmonthly(func)
	else: return repeatmonthly(func)

def daily(func):
	"""Decorator for daily functions. Depending on configuration, is equivalent to either :meth:`rundaily` or :meth:`repeatdaily`."""
	if config["autostart"]: return rundaily(func)
	else: return repeatdaily(func)

def hourly(func):
	"""Decorator for hourly functions. Depending on configuration, is equivalent to either :meth:`runhourly` or :meth:`repeathourly`."""
	if config["autostart"]: return runhourly(func)
	else: return repeathourly(func)
###


intervals = {
	'yearly':{
		'getnext':lambda now:datetime.datetime(now.year+1,1,1,tzinfo=tz()),
		'variation':(15,200),
		'functions':[]
	},
	'monthly':{
		'getnext':lambda now:datetime.datetime(now.year,now.month + 1,1,tzinfo=tz()) if now.month != 12 else datetime.datetime(now.year+1,1,1,tzinfo=tz()),
		'variation':(15,100),
		'functions':[]
	},
	'daily':{
		'getnext':lambda now:datetime.datetime(now.year,now.month,now.day,tzinfo=tz()) + datetime.timedelta(days=1),
		'variation':(10,50),
		'functions':[]
	},
	'hourly':{
		'getnext':lambda now:datetime.datetime(now.year,now.month,now.day,now.hour,tzinfo=tz()) + datetime.timedelta(hours=1),
		'variation':(5,20),
		'functions':[]
	},
	# just for testing
	'constantly':{
		'getnext':lambda now:datetime.datetime.now(tz=tz()) + datetime.timedelta(seconds=10),
		'variation':(1,2),
		'functions':[]
	}
}


def doreah_regular_daemon(interval):
	while True:
		now = datetime.datetime.now(tz=tz())
		next = intervals[interval]['getnext'](now)

		diff = int(next.timestamp() - now.timestamp())
		rand = random.randint(*intervals[interval]['variation'])
		wait = diff + rand

		time.sleep(wait)
		for f in intervals[interval]['functions']:
			try:
				f['function'](*f['args'],**f['kwargs'])
			except Exception as e:
				print(e)
			time.sleep(2)


for interval in intervals:
	intervals[interval]['thread'] = Thread(target=doreah_regular_daemon,kwargs={'interval':interval})
	intervals[interval]['thread'].daemon = True
	intervals[interval]['thread'].setName(f"doreah-regular-{interval}")
	intervals[interval]['thread'].start()


def run_regularly(interval,func):

	functioninfo = {
		'function':func,
		'args':(),
		'kwargs':{}
	}

	# run it once
	t = Timer(5,**functioninfo)
	t.daemon = True
	t.start()

	# add to list
	intervals[interval]['functions'].append(functioninfo)

	# return unchanged function
	return func

def repeat_regularly(interval,func):

	def self_scheduling_func(*args,**kwargs):

		functioninfo = {
			'function':func,
			'args':args,
			'kwargs':kwargs
		}

		# execute function
		func(*args,**kwargs)

		# add original function to list, with args and kwargs from first invocation
		intervals[interval]['functions'].append(functioninfo)

	return self_scheduling_func


def runyearly(func):
	"""Decorator to make the function execute on first definition as well as every year."""
	return run_regularly('yearly',func)


def repeatyearly(func):
	"""Decorator to make the function repeat every new year after being called once."""
	return repeat_regularly('yearly',func)

def runmonthly(func):
	"""Decorator to make the function execute on first definition as well as every month."""
	return run_regularly('monthly',func)

def repeatmonthly(func):
	"""Decorator to make the function repeat every new month after being called once."""
	return repeat_regularly('monthly',func)

def rundaily(func):
	"""Decorator to make the function execute on first definition as well as every day."""
	return run_regularly('daily',func)

def repeatdaily(func):
	"""Decorator to make the function repeat every new day after being called once."""
	return repeat_regularly('daily',func)

def runhourly(func):
	"""Decorator to make the function execute on first definition as well as every hour."""
	return run_regularly('hourly',func)

def repeathourly(func):
	"""Decorator to make the function repeat every new hour after being called once."""
	return repeat_regularly('hourly',func)

# just for testing
def runoften(func):
	return run_regularly('constantly',func)
