from bs4 import BeautifulSoup
from copy import deepcopy
import re
import os

from ._internal import DEFAULT, defaultarguments, DoreahConfig


config = DoreahConfig("pyhp",
	interpret=str
)





@defaultarguments(config,interpret="interpret")
def file(path,d={},interpret=DEFAULT,noroot=False):
	"""Parses a pyhp source file and returns the generated html code.

	:param string path: Location of the pyhp source file
	:param dict d: Variables dictionary
	:param function interpret: Function that determines string representations of variables
	:return: HTML source
	"""

	with open(path,"r") as f:
		content = f.read()

	directory = os.path.dirname(os.path.abspath(path))

	return parse(content,d,interpret=interpret,directory=directory,noroot=noroot)


def _file(path,d,interpret=DEFAULT,noroot=False):

	with open(path,"r") as f:
		content = f.read()

	directory = os.path.dirname(os.path.abspath(path))

	return _parse(content,d,interpret=interpret,directory=directory,noroot=noroot)


@defaultarguments(config,interpret="interpret")
def parse(src,d={},interpret=DEFAULT,directory=None,noroot=False):
	"""Parses pyhp source and returns the generated html code.

	:param string src: Source string
	:param dict d: Variables dictionary
	:param function interpret: Function that determines string representations of variables
	:return: HTML source
	"""

	doc = _parse(src,d,interpret=interpret,directory=directory,noroot=noroot)


	#raw = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
	#raw = etree.tostring(doc,encoding="unicode",method="html").replace("&gt;",">").replace("&lt;","<")
	return doc.decode()

# to tree
def _parse(src,d,interpret=DEFAULT,directory=None,noroot=False):

	doc = BeautifulSoup(src,"html.parser")
	doc = _parse_node(doc,d,interpret,directory=directory)[0]
	#result = list(doc.children)

	if noroot:
		return list(doc.children)
	else:
		return doc


def _parse_node(node,d,interpret,directory=None):

	if isinstance(node,str): return [node]


	## parse pyhp nodes

	if node.name == "pyhp":

		### CODE

		if len(node.attrs) == 0:
			#print("Executing code!")
			#print({k:d[k] for k in d if not k.startswith("_")})
			code = list(node.children)[0]
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

			exec(code,d)

			return []

		#### SAVE

		if _attr(node,"save") is not None and _attr(node,"as") is not None:
			#print("d[" + _attr(node,"as") + "] = " + _attr(node,"save"))
			d[_attr(node,"as")] = eval(_attr(node,"save"),d)
			#print({k:d[k] for k in d if not k.startswith("_")})

			return []

		### IMPORT

		if _attr(node,"import") is not None:
			exec("import " + _attr(node,"import"),d)

			return []


		#### INCLUDE

		elif _attr(node,"include") is not None:

			filename = _attr(node,"include")
			if directory is None:
				# relative to execution path
				filename = filename
			else:
				# relative to this file
				filename = os.path.join(directory,filename)


			try:
				subnodes = _file(filename,d,interpret=interpret,noroot=True)
				for attr in node.attrs:
					# give attributes to included first top node
					if attr != "include":
						subnodes[0].attrs[attr] = _attr(node,attr)
				return subnodes
			except:
				raise
				return []


		#### IF

		elif _attr(node,"if") is not None:
			if eval(_attr(node,"if"),d):
				nodestoreturn = []
				for sn in node:
					nodestoreturn += _parse_node(sn,d,interpret,directory=directory)
				return nodestoreturn
			else:
				return []


		#### FOR IN

		elif _attr(node,"for") is not None and _attr(node,"in") is not None:
			nodestoreturn = []
			# for loop of the elements
			first = True
			try:
				elements = eval(_attr(node,"in"),d)
			except:
				# allow invalid expressions in for loops, just ignore them
				elements = []
			for element in elements:
				if not first and _attr(node,"separator") is not None:
					nodestoreturn += [_attr(node,"separator")]
				first = False

				# in case we overload a dict entry, keep the old one
				sentinel = object()
				if _attr(node,"for") in d:
					hide = d[_attr(node,"for")]
				else:
					hide = sentinel

				# the dict needs to remain the same object so changes from one node
				# in the for loop are carried over into the next loop
				d.update({_attr(node,"for"):element})

				# now go through the nodes each time
				for sn in node:
					nodestoreturn += _parse_node(deepcopy(sn),d,interpret,directory=directory)

				# clear the variable after each loop
				del d[_attr(node,"for")]
				if hide is not sentinel:
					d[_attr(node,"for")] = hide


			return nodestoreturn


		#### ECHO

		elif _attr(node,"echo") is not None:
			return BeautifulSoup(interpret(eval(_attr(node,"echo"),d)),"html.parser")
			#return [interpret(eval(_attr(node,"echo"),d))]


		else:
			print("Not a valid pyhp tag!")
			return []


	## parse normal nodes

	else:

		## replace attributes (not necessary in pyhp nodes)

		if hasattr(node,"attrs"):
			for name,value in node.attrs.items():
				if isinstance(value,list): value = " ".join(value)
				vars = re.findall("{.*?}",value)
				for v in vars:
					vname = v[1:-1]
					try:
						value = value.replace(v,interpret(eval(vname,d)))
					except:
						pass
						print("Error parsing:",v,"in attribute")

				node.attrs[name] = value



		subnodes = [n for n in node]
		newsubnodes = []
		for subnode in subnodes:
			sn = subnode.extract()
			newsubnodes += _parse_node(sn,d,interpret,directory=directory)

		for nsn in newsubnodes:
			node.append(nsn)


		return [node]



def _attr(node,name):
	res = node.get(name)
	try:
		return res.replace(" gr "," > ").replace(" ls "," < ")
	except:
		return res





### run test server

if __name__ == "__main__":
	from bottle import get, run, static_file
	from doreah.pyhp import file
	import os

	@get("/<path:path>")
	def serve_file(path):

		if os.path.exists(path + ".pyhp"):
			return file(path + ".pyhp")
		if os.path.exists(path):
			return static_file(path,root="")
		if os.path.exists(path + ".html"):
			return static_file(path + ".html",root="")

		return static_file(path,root="") # will produce proper error


	run(host="::",port=1337)
