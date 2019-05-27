import requests
import mechanicalsoup
import json
import lxml
from lxml import html
import math
import re

from ._internal import DEFAULT, defaultarguments, doreahconfig

_config = {}

def config(attempts=10):
	"""Configures default values for this module.

	These defaults define behaviour of function calls when respective arguments are omitted. Any call of this function will overload the configuration in the .doreah file of the project. This function must be called with all configurations, as any omitted argument will reset to default, even if it has been changed with a previous function call."""
	global _config
	_config["attempts"] = attempts


config()




def parse(initial,steps):
	"""Takes a html node and applies all supplied steps to it.

	:param xmlnode initial: Node to start parsing from
	:param list steps: Parsing steps
	:returns: The resulting node or string value
	"""

	i = 0
	result = initial
	has_split = False
	for step in steps:
		steptype,instruction = step.get("type"),step.get("instruction")
		if not has_split:
			if steptype == "xpath":
				result = result.xpath(instruction)[0]
			elif steptype == "prefix":
				result = instruction + result
			elif steptype == "suffix":
				result = result + instruction
			elif steptype == "rmprefix":
				if result.startswith(instruction): result = result.replace(instruction,"",1)
			elif steptype == "regex":
				result = re.sub(instruction,r"\1",result)
			elif steptype == "last":
				result = result.split(instruction)[-1]


			# these are only applicable for single entries
			elif steptype == "split":
				result = result.split(instruction)
				has_split = True
			elif steptype == "makelist":
				result = [result]
				has_split = True
			elif steptype == "xpathls":
				result = result.xpath(instruction)
				has_split = True
			elif steptype == "follow":
				br = mechanicalsoup.StatefulBrowser()
				page = br.open(result)
				result = html.fromstring(page.content)

		else:
			if steptype == "pick":
				result = result[instruction]
				has_split = False
			elif steptype == "combine":
				result = instruction.join(result)
				has_split = False

			else:

				for k in range(len(result)):
					if steptype == "xpath":
						result[k] = result[k].xpath(instruction)[0]
					elif steptype == "prefix":
						result[k] = instruction + result[k]
					elif steptype == "suffix":
						result[k] = result[k] + instruction
					elif steptype == "rmprefix":
						if result[k].startswith(instruction): result[k] = result[k].replace(instruction,"",1)
					elif steptype == "regex":
						result[k] = re.sub(instruction,r"\1",result[k])
					elif steptype == "last":
						result[k] = result[k].split(instruction)[-1]

		i += 1

	return result

@defaultarguments(_config,attempts="attempts")
def scrape(url,steps,requires_javascript=False,attempts=DEFAULT):
	"""Scrapes the given URL with the supplied steps and returns the result.

	:param string url: URL to scrape
	:param list steps: Steps to apply to the top node of the document
	:param bool requires_javascript: Whether the page as it displays in a js-enabled browser should be scraped or merely the source
	:return: Resulting node or string
	"""

	#print("Scraping",url)

	if requires_javascript:
		tree = _scrape_selenium(url)
	else:
		tree = _scrape_soup(url,attempts=attempts)


	return parse(tree,steps)


class _GoodException(Exception):
	pass

@defaultarguments(_config,attempts="attempts")
def scrape_all(base_url,steps_elements,steps_content,start_page=0,page_multiplier=1,stop=math.inf,stopif={},attempts=DEFAULT,requires_javascript=False):
	"""Function to scrape a library, gallery or feed that consists of well-patterned elements and return all elements
	represented by the specified attributes and contents.

	:param string base_url: The URL part all pages have in common, with {page} as a placeholder for the page
	:param list steps_elements: Steps from the document node to get a list of all elements to be scraped
	:param dict steps_content: For each desired information about each element, a list of steps to reach this information from the element node
	:param string/int start_page: The part that must be supplied to the URL to get the first page
	:param int/func page_multiplier: Either an integer that the page needs to be multiplied with to get the correct URL, or a function that takes the page number as argument
	:param int stop: Limit of elements to scrape
	:param dict stopif: For any element attribute, a function that evaluates to True if scraping should be stopped
	:param int attempts: How many times a page visit should be attempted
	:return: A list of all elements as dictionaries of their attributes

	"""

	# set the page function
	if isinstance(page_multiplier,int):
		getpage = lambda x: x*page_multiplier
	else:
		getpage = page_multiplier


	pagenum = 0
	returned = 0

	try:
		while returned < stop:
			url = base_url.format(page=getpage(pagenum))

			#print("Page",pagenum,"URL",url)
			elements = scrape(url,steps_elements,attempts=attempts)
			#print(len(elements),"on this page")

			for e in elements:
				if returned >= stop: raise Exception("Number of elements reached")
				resultelement = {}

				for attribute in steps_content:
					#print("Attribute",attribute)
					res = parse(e,steps_content[attribute])
					#print("Setting attribute",attribute,"to",res)
					if attribute in stopif and stopif[attribute](res):
						raise Exception("Break condition reached")
					resultelement[attribute] = res

				#result.append(resultelement)
				yield resultelement
				returned += 1

			pagenum += 1

	except _GoodException:
		pass
	except:
		raise






def _scrape_soup(url,attempts):
	br = mechanicalsoup.StatefulBrowser()
	for attempt in range(attempts):
		try:
			page = br.open(url)
			tree = html.fromstring(page.content)
			break
		except:
			print("Problem while scraping",url)
			time.sleep(1 + attempt)
	return tree


def _scrape_selenium(url):
	try:
		from selenium import webdriver
		dr = webdriver.Firefox()
	except:
		print("Selenium and the Firefox web driver are needed to scrape sites with javascript")
		return None

	dr.get(url)
	raw = dr.execute_script("return document.documentElement.outerHTML")
	tree = html.fromstring(raw)
	dr.close()
	return tree
























# now check local configuration file
_config.update(doreahconfig("scraping"))
