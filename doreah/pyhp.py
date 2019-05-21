from lxml import etree
from copy import deepcopy
import re
import os

from ._internal import DEFAULT, defaultarguments, doreahconfig

_config = {}


# set configuration
def config(interpret=str):
	"""Configures default values for this module.

	These defaults define behaviour of function calls when respective arguments are omitted. Any call of this function will overload the configuration in the .doreah file of the project. This function must be called with all configurations, as any omitted argument will reset to default, even if it has been changed with a previous function call."""
	global _config
	_config["interpret"] = interpret

# initial config on import, set everything to default
config()





@defaultarguments(_config,interpret="interpret")
def file(path,d,interpret=DEFAULT,noroot=False):
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


@defaultarguments(_config,interpret="interpret")
def parse(src,d,interpret=DEFAULT,directory=None,noroot=False):
	"""Parses pyhp source and returns the generated html code.

	:param string src: Source string
	:param dict d: Variables dictionary
	:param function interpret: Function that determines string representations of variables
	:return: HTML source
	"""

	doc = _parse(src,d,interpret=interpret,directory=directory,noroot=noroot)


	#raw = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
	raw = etree.tostring(doc,encoding="unicode",method="html").replace("&gt;",">").replace("&lt;","<")


	return raw
	# yes I know
	# it's a temporary thing okay

# to tree
def _parse(src,d,interpret=DEFAULT,directory=None,noroot=False):

	if noroot:
		# pseudo root
		src = "<pseudoroot>" + src + "</pseudoroot>"

	doc = etree.XML(src)
	doc = _parse_node(doc,d,interpret,directory=directory)[0]

	if noroot:
		return list(doc) #all child elements

	return doc


def _parse_node(node,d,interpret,directory=None):


	## fix
	#if node.tag == "html":
	#	node.attrib["xmlns"] = "http://www.w3.org/1999/xhtml"


	## parse pyhp nodes

	if node.tag == "pyhp":

		#### SAVE

		if _attr(node,"save") is not None and _attr(node,"as") is not None:
			print("d[" + _attr(node,"as") + "] = " + _attr(node,"save"))
			d[_attr(node,"as")] = eval(_attr(node,"save"),d)

			return [node.tail]



		#### INCLUDE

		elif _attr(node,"include") is not None:
			filename = _attr(node,"include")
			if directory is None:
				# relative to execution path
				filename = filename
			else:
				# relative to this file
				filename = os.path.join(directory,filename)

			#with open(filename,"r") as f:
			#	raw = f.read()

			subnodes = _file(filename,d,interpret=interpret,noroot=True)
			print(subnodes)

			return subnodes + [node.tail]


		#### IF

		elif _attr(node,"if") is not None:
			if eval(_attr(node,"if"),d):
				nodestoreturn = [node.text]
				for sn in node:
					nodestoreturn += _parse_node(sn,d,interpret,directory=directory)
				nodestoreturn += [node.tail]
				return nodestoreturn
			else:
				return [node.tail]


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

				# now go through the nodes each time
				nodestoreturn += [node.text]

				for sn in node:

					# parse with the normal dict and the current element of the loop
					sn = deepcopy(sn)
					nodestoreturn += _parse_node(sn,{**d, **{_attr(node,"for"):element}},interpret,directory=directory)



			nodestoreturn += [node.tail]

			return nodestoreturn


		#### ECHO

		elif _attr(node,"echo") is not None:
			#return [d.get(node.get("echo"))]
			return [interpret(eval(_attr(node,"echo"),d))] + [node.tail]

		return []


	## parse normal nodes

	else:

		## replace attributes (not necessary in pyhp nodes)

		for name,value in node.attrib.items():
			vars = re.findall("{.*?}",value)
			for v in vars:
				vname = v[1:-1]
				try:
					value = value.replace(v,interpret(eval(vname,d)))
				except:
					pass

			node.attrib[name] = value



		subnodes = [n for n in node]
		newsubnodes = []
		for subnode in subnodes:
			node.remove(subnode)
			newsubnodes += _parse_node(subnode,d,interpret,directory=directory)

		prev = None
		for nsn in newsubnodes:


			if nsn is None: continue

			if isinstance(nsn,str):

				# string nodes need to be either the tail of their previous node, or if they're
				# in first position, the text of the parent node
				if prev is None:
					#if node.tag == "head": print(str(nsn) + " appended as text to " + str(node))
					try:
						node.text += nsn
					except:
						node.text = nsn
				else:
					#if node.tag == "head": print(str(nsn) + " appended as tail to " + str(prev))
					try:
						prev.tail += nsn
					except:
						prev.tail = nsn
			else:
				# once we encounter a real node, we can set it as prev for all following text nodes
				prev = nsn



		for nsn in newsubnodes:
			if isinstance(nsn,etree._Element):
				node.append(nsn)

		if node.tag == "head":
			#print(newsubnodes)

			print(etree.tostring(node))

		return [node]



def _attr(node,name):
	res = node.get(name)
	try:
		return res.replace(" gr "," > ").replace(" ls "," < ")
	except:
		return res



# now check local configuration file
_config.update(doreahconfig("pyhp"))
