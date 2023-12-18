from ._color import _ANSICOLOR
from getpass import getpass


YESVALUES = ["y","yes","yea","1","positive","true"]
NOVALUES = ["n","no","nay","0","negative","false"]


def ask(msg,default=True,repeat=False,skip=False):
	"""Offers a prompt that the user may answer with yes or no.

	:param string msg: The prompt message
	:param boolean default: Which response (True/False) should be assumed if none is given. Can be set no None to not accept implicit answers.
	:param boolean repeat: Whether the prompt should be repeated until a valid response is acquired. Otherwise, will return None.
	:param boolean skip: Literally just skips the whole thing and returns default anyway.
	:return: Boolean value of the user's choice, or None if invalid response
	"""

	if skip: return default

	if default is None:
		a = "[y/n]"
	elif default:
		a = "[Y/n]"
	else:
		a = "[y/N]"

	print(msg,a)

	inp = input()
	if inp.lower() in YESVALUES:
		return True
	elif inp.lower() in NOVALUES:
		return False
	elif inp == "" and default is not None:
		return default
	else:
		print("Not a valid response")
		if repeat:
			return ask(msg,default,repeat)
		else:
			return None


def prompt(msg,types=(str,),default=None,repeat=False,skip=False,secret=False):
	"""Offers a prompt that allows custom input.

	:param string msg: The prompt message
	:param types: Accepted response types in order of priority
	:param default: Response that should be assumed if no input is given.
	:param boolean repeat: Whether the prompt should be repeated until a valid response is acquired. Otherwise, will return None.
	:param boolean skip: Literally just skips the whole thing and returns default anyway.
	:param boolean secret: Don't show user input (e.g. passwords)
	:return: User's choice, or None if invalid response and no default
	"""

	if skip: return default

	print(msg)

	inp = getpass("") if secret else input()

	if inp != "":
		for t in types:
			try:
				return t(inp)
			except (TypeError, ValueError):
				pass
		print("Not a valid response")
		if repeat:
			return prompt(msg,types=types,default=default,repeat=repeat,secret=secret)
		else:
			return default

	elif inp == "":
		if repeat and default is None:
			return prompt(msg,types=types,default=default,repeat=repeat,secret=secret)
		else:
			return default


def ellipsis(txt,length,padded=False):
	if len(txt) > length: return txt[:length-3] + "..."
	else:
		if padded:
			while len(txt) < length: txt += " "
		return txt



###
## COLORED OUTPUT
####

# weird construct to enable quick function calls like col["yellow"](txt)
class _Col:
	def __getitem__(self, color):
		def colored(txt,c=color):
			pre,post = _ANSICOLOR(c)
			return pre + str(txt) + post

		return colored

col = _Col()







###
## PROGRESS BARS
###

# credit to StackOverflow user Greenstick
def print_progress_bar(num=None,prct=None,prefix="",suffix="",decimals=0,length=100,fill="█",manualend=False):
	if num is not None and num[1] == 0: prct = 1
	if prct is None: prct = num[0] / num[1]
	percent = ("{0:." + str(decimals) + "f}").format(100 * prct)
	filledLength = int(length * prct)
	bar = fill * filledLength + '-' * (length - filledLength)
	print('\r%s |%s| %s%% %s' % (prefix, bar, percent, ellipsis(suffix,50,padded=True)), end = '\r')
	#print(num)
	# Print New Line on Complete
	if prct == 1 and not manualend:
		print()


class ProgressBar:
	def __init__(self,max,prefix="",decimals=0,length=100,fill="█"):
		self.max = max
		self.prefix = prefix
		self.decimals = decimals
		self.length = length
		self.fill = fill
		self.current = 0
		self.step = ""
		self.finished = False

	def prnt(self,prct=None,num=None,manualend=False):
		print_progress_bar(prct=prct,num=num,prefix=self.prefix,suffix=self.step,decimals=self.decimals,length=self.length,fill=self.fill,manualend=manualend)

	def print(self):
		self.prnt(num=(self.current,self.max))

	def progress(self,num=1,step=""):
		self.current += num
		self.step = step
		self.print()
		if self.current == self.max: self.finished = True

	def done(self):
		self.current = self.max
		self.step = ""
		if not self.finished:
		#self.step = "Done!"
			self.print()
			self.finished = True


class NestedProgressBar(ProgressBar):
	def __init__(self,max,prefix="",decimals=0,length=100,fill="█",manual=False):
		self.layers = [[0,max]]
		self.prefix = prefix
		self.decimals = decimals
		self.length = length
		self.fill = fill
		self.step = ""
		self.manual = manual

	def print(self):
		prct = 0
		layervalue = 1
		for l in self.layers:
			part = layervalue / l[1] # how much of the bar is at stake per unit of this layer
			prct += part * l[0] # so much needs to be added because of current progress
			layervalue = part # one part will be analyzed on the next layer
		self.prnt(prct=prct,manualend=True)
		#print(self.layers,self.step)
		# Print New Line on Complete
		if self.layers[0][0] == self.layers[0][1]:
			print()

	def godeeper(self,max):
		self.layers.append([0,max])
		if max == 0: self.layers[-1] = [1,1] # already done because empty

	def done(self):
		self.layers.pop()
		self.progress()


	def progress(self,num=1,step=""):
		self.step = step
		self.layers[-1][0] += num
		self.print()
		if self.layers[-1][0] == self.layers[-1][1] and not self.manual: self.done()
