from lxml import etree
from copy import deepcopy
import re

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
def file(path,d,interpret=DEFAULT):
	"""Parses a pyhp source file and returns the generated html code.

	:param string path: Location of the pyhp source file
	:param dict d: Variables dictionary
	:param function interpret: Function that determines string representations of variables
	:return: HTML source
	"""

	with open(path,"r") as f:
		content = f.read()

	return parse(content,d,interpret=interpret)


@defaultarguments(_config,interpret="interpret")
def parse(src,d,interpret=DEFAULT):
	"""Parses pyhp source and returns the generated html code.

	:param string src: Source string
	:param dict d: Variables dictionary
	:param function interpret: Function that determines string representations of variables
	:return: HTML source
	"""
	doc = etree.XML(src)

	doc = _parse_node(doc,d,interpret)[0]

	return etree.tostring(doc)


def _parse_node(node,d,interpret):

	## replace attributes

	for name,value in node.attrib.items():
		vars = re.findall("{.*?}",value)
		for v in vars:
			vname = v[1:-1]
			value = value.replace(v,interpret(eval(vname,d)))

		node.attrib[name] = value

	## parse pyhp nodes

	if node.tag == "pyhp":

		#### IF

		if _attr(node,"if") is not None:
			if eval(_attr(node,"if"),d):
				nodestoreturn = [node.text]
				for sn in node:
					nodestoreturn += _parse_node(sn,d,interpret)
				nodestoreturn += [node.tail]
				return nodestoreturn
			else:
				return [node.tail]


		#### FOR IN

		elif _attr(node,"for") is not None and _attr(node,"in") is not None:
			nodestoreturn = []
			# for loop of the elements
			for element in eval(_attr(node,"in"),d):
				# now go through the nodes each time
				nodestoreturn += [node.text]
				for sn in node:
					# parse with the normal dict and the current element of the loop
					sn = deepcopy(sn)
					nodestoreturn += _parse_node(sn,{**d, **{_attr(node,"for"):element}},interpret)
			nodestoreturn += [node.tail]

			return nodestoreturn


		#### ECHO

		elif _attr(node,"echo") is not None:
			#return [d.get(node.get("echo"))]
			return [interpret(eval(_attr(node,"echo"),d))] + [node.tail]

		return []


	## parse normal nodes

	else:
		subnodes = [n for n in node]
		newsubnodes = []
		for subnode in subnodes:
			node.remove(subnode)
			newsubnodes += _parse_node(subnode,d,interpret)

		prev = None
		for nsn in newsubnodes:

			if isinstance(nsn,str):
				if nsn is None: continue
				# string nodes need to be either the tail of their previous node, or if they're
				# in first position, the text of the parent node
				if prev is None:
					try:
						node.text += nsn
					except:
						node.text = nsn
				else:
					try:
						prev.tail += nsn
					except:
						prev.tail = nsn
			else:
				# once we encounter a real node, we can set it as prev for all following text nodes
				prev = nsn

		for nsn in newsubnodes:
			if not isinstance(nsn,str) and nsn is not None:
				node.append(nsn)

		return [node]



def _attr(node,name):
	res = node.get(name)
	try:
		return res.replace(" gr "," > ").replace(" ls "," < ")
	except:
		return res



# now check local configuration file
_config.update(doreahconfig("pyhp"))
