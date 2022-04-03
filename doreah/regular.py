from threading import Thread, Timer
import datetime
import random

from ._internal import DEFAULT, defaultarguments, gopen, DoreahConfig



config = DoreahConfig("regular",
	offset=0
)

def tz():
	return datetime.timezone(offset=datetime.timedelta(hours=config["offset"]))


def runyearly(func):
	"""Decorator to make the function execute on first definition as well as every year."""

	def self_scheduling_func():
		# execute function
		func()

		# schedule next execution
		now = datetime.datetime.now(tz=tz())
		nextyear = datetime.datetime(now.year+1,1,1,tzinfo=tz())
		wait = nextyear.timestamp() - now.timestamp() + random.randint(20,200)
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
		now = datetime.datetime.now(tz=tz())
		nextyear = datetime.datetime(now.year+1,1,1,tzinfo=tz())
		wait = nextyear.timestamp() - now.timestamp() + random.randint(20,200)
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
		now = datetime.datetime.now(tz=tz())
		nextmonth = datetime.datetime(now.year,now.month + 1,1,tzinfo=tz()) if now.month != 12 else datetime.datetime(now.year+1,1,1,tzinfo=tz())
		wait = nextmonth.timestamp() - now.timestamp() + random.randint(20,100)
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
		now = datetime.datetime.now(tz=tz())
		nextmonth = datetime.datetime(now.year,now.month + 1,1,tzinfo=tz()) if now.month != 12 else datetime.datetime(now.year+1,1,1,tzinfo=tz())
		wait = nextmonth.timestamp() - now.timestamp() + random.randint(20,100)
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
		now = datetime.datetime.now(tz=tz())
		nextday = datetime.datetime(now.year,now.month,now.day,tzinfo=tz()) + datetime.timedelta(days=1)
		wait = nextday.timestamp() - now.timestamp() + random.randint(10,50)
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
		now = datetime.datetime.now(tz=tz())
		nextday = datetime.datetime(now.year,now.month,now.day,tzinfo=tz()) + datetime.timedelta(days=1)
		wait = nextday.timestamp() - now.timestamp() + random.randint(10,50)
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
		wait = nexthour.timestamp() - now.timestamp() + random.randint(5,25)
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
		wait = nexthour.timestamp() - now.timestamp() + random.randint(5,25)
		Timer(wait,self_scheduling_func,args=args,kwargs=kwargs).start()

	def starter(*args,**kwargs):
		t = Thread(target=self_scheduling_func,args=args,kwargs=kwargs)
		t.daemon = True
		t.start()
	return starter
