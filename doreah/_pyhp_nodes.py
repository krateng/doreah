from .pyhp3 import pyhpnode
import os


@pyhpnode("Code")
def handle():
	code = list(children)[0]
	code = code.strip("\t").strip(" ")
	code = code.split("\n")
	if len(code) == 1:
		# one-line code
		code = code[0]
	else:
		# multiline code
		if code[0] != "" or code[-1] != "":
			print("Malformed code block!")
		code = code[1:-1]
		roottabs = 0
		for char in code[0]:
			if char == "\t" or char == " ":
				roottabs += 1
			else:
				break

		code = [line[roottabs:] for line in code]
		code = "\n".join(code)

	exec(code,environment)

	return []

#### SAVE
@pyhpnode("VariableAssign")
def handle(save_,as_):
	#print("d[" + _attr(node,"as") + "] = " + _attr(node,"save"))
	environment[as_] = eval(save_,environment)
	#print({k:d[k] for k in d if not k.startswith("_")})

	return []


### IMPORT
@pyhpnode("Import")
def handle(import_):
	exec("import " + import_,environment)

	return []


#### INCLUDE
@pyhpnode("Include")
def handle(include_,with_=None):

	filename = include_
	if directory is None:
		# relative to execution path
		filename = filename
	else:
		# relative to this file
		filename = os.path.join(directory,filename)


	if with_ is not None:

		localdict = eval(with_,environment)
		hidedict = {}
		# save overridden variables
		for key in localdict:
			if key in environment:
				hidedict[key] = environment[key]
		environment.update(localdict)




	try:
		subnodes = _file(filename,environment,interpret=interpret,noroot=True)
		for attr in node.attrs:
			# give attributes to included first top node
			if attr not in ["with","include"]:
				subnodes[0].attrs[attr] = _attr(node,attr)

	except:
		print("Could not include",filename)
		raise
		subnodes = []

	if with_ is not None:
		# restore outer environment
		for key in localdict:
			del environment[key]
		for key in hidedict:
			environment[key] = hidedict[key]

	return subnodes


#### IF
@pyhpnode("If")
def handle(if_):
	if eval(if_,environment):
		nodestoreturn = []
		for sn in node:
			nodestoreturn += _parse_node(sn,d,interpret,directory=directory)
		return nodestoreturn
	else:
		return []


#### FOR IN
@pyhpnode("ForIn")
def handle(for_,in_,separator_=None):
	nodestoreturn = []
	# for loop of the elements
	first = True
	try:
		elements = eval(in_,environment)
	except:
		# allow invalid expressions in for loops, just ignore them
		elements = []
	for element in elements:
		if not first and separator_ is not None:
			nodestoreturn += [separator_]
		first = False

		# in case we overload a dict entry, keep the old one
		sentinel = object()
		if for_ in environment:
			hide = environment[for_]
		else:
			hide = sentinel

		# the dict needs to remain the same object so changes from one node
		# in the for loop are carried over into the next loop
		environment.update({for_:element})

		# now go through the nodes each time
		for sn in node:
			nodestoreturn += _parse_node(deepcopy(sn),environment,interpret,directory=directory)

		# clear the variable after each loop
		del environment[for_]
		if hide is not sentinel:
			environment[for_] = hide


	return nodestoreturn


### LOCAL SCOPE
@pyhpnode("With")
def handle(with_):

	localdict = eval(with_,environment)
	hidedict = {}

	# save overridden variables
	for key in localdict:
		if key in environment:
			hidedict[key] = environment[key]

	d.update(localdict)

	nodestoreturn = []
	for sn in node:
		nodestoreturn += _parse_node(deepcopy(sn),environment,interpret,directory=directory)

	# restore outer environment
	for key in localdict:
		del environment[key]
	for key in hidedict:
		environment[key] = hidedict[key]

	return nodestoreturn


#### ECHO
@pyhpnode("Echo")
def handle(echo_):
	return BeautifulSoup(interpret(eval(echo_,environment)),"html.parser")
	#return [interpret(eval(_attr(node,"echo"),d))]
