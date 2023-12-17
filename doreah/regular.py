from threading import Thread, Timer
import datetime
import time


intervals = {
	'yearly':{
		'getnext':lambda now:datetime.datetime(now.year+1,1,1),
		'functions':[]
	},
	'monthly':{
		'getnext':lambda now:datetime.datetime(now.year,now.month + 1,1) if now.month != 12 else datetime.datetime(now.year+1,1,1),
		'functions':[]
	},
	'daily':{
		'getnext':lambda now:datetime.datetime(now.year,now.month,now.day) + datetime.timedelta(days=1),
		'functions':[]
	},
	'hourly':{
		'getnext':lambda now:datetime.datetime(now.year,now.month,now.day,now.hour) + datetime.timedelta(hours=1),
		'functions':[]
	},
	# just for testing
	'constantly':{
		'getnext':lambda now:datetime.datetime.now() + datetime.timedelta(seconds=1),
		'functions':[]
	}
}


# init daemon for each interval
# spawns all runs, then goes to sleep until next time
def doreah_regular_daemon(interval):
	i = 0
	while True:
		i += 1
		now = datetime.datetime.now()
		next = intervals[interval]['getnext'](now)

		wait = int(next.timestamp() - now.timestamp()) + 5

		time.sleep(wait)
		for f in intervals[interval]['functions']:
			try:
				t = Thread(target=f['function'],args=f['args'],kwargs=f['kwargs'])
				t.daemon = False
				t.name = f"doreah-regular-{interval}-loop{i}-{f['function'].__name__}"
				t.start()
			except Exception as e:
				print(e)
			time.sleep(2)


# spawns above init daemons if any functions actually need it
def spawn_all_needed():

	for interval in intervals:
		data = intervals[interval]
		if len(data['functions']) > 0 and not data.get('thread'):
			data['thread'] = Thread(target=doreah_regular_daemon,kwargs={'interval':interval})
			data['thread'].daemon = True
			data['thread'].name = f"doreah-regular-{interval}-daemon"
			data['thread'].start()


def run_regularly(interval,func):

	functioninfo = {
		'function':func,
		'args':(),
		'kwargs':{}
	}

	# add to list
	intervals[interval]['functions'].append(functioninfo)
	spawn_all_needed()

	# run it once
	t = Timer(5,**functioninfo)
	t.daemon = True
	t.start()

	# return unchanged function
	return func


def repeat_regularly(interval,func):

	def self_scheduling_func(*args,**kwargs):

		functioninfo = {
			'function':func,
			'args':args,
			'kwargs':kwargs
		}

		# add original function to list, with args and kwargs from first invocation
		intervals[interval]['functions'].append(functioninfo)
		spawn_all_needed()

		# execute function once
		func(*args,**kwargs)

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
