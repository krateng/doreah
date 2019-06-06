from ._internal import DEFAULT, defaultarguments, DoreahConfig


config = DoreahConfig("io")
config._initial(yesvalues=["y","yes","yea","1","positive","true"],novalues=["n","no","nay","0","negative","false"])



def ask(msg,default=True,repeat=False):
	"""Offers a prompt that the user may answer with yes or no.

	:param string msg: The prompt message
	:param boolean default: Which response (True/False) should be assumed if none is given. Can be set no None to not accept implicit answers.
	:param boolean repeat: Whether the prompt should be repeated until a valid response is acquired. Otherwise, will return None.
	:return: Boolean value of the user's choice, or None if invalid response
	"""
	if default is None:
		a = "[y/n]"
	elif default:
		a = "[Y/n]"
	else:
		a = "[y/N]"

	print(msg,a)

	inp = input()
	if inp.lower() in config["yesvalues"]:
		return True
	elif inp.lower() in config["novalues"]:
		return False
	elif inp == "" and default is not None:
		return default
	else:
		print("Not a valid response")
		if repeat:
			return ask(msg,default,repeat)
		else:
			return None
