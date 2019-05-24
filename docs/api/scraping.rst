Scraping
==============

How To
---------------

Step Instructions
^^^^^^^^^^^^^^^^^^^^^

This module provides a simplified interface to parse XML trees with a set of predefined steps.
These need to be supplied in a list as dicts with the keys `steptype` and 'instruction', although
the second may be omitted for steps that do not have any further instructions.

The following steps are possible:
* Steps that work for both single elements and lists:
		xpath
			follows the xpath down the tree, returns first element (node -> node or string)
		prefix
			adds a prefix to the string (string -> string)
		suffix
			appends a suffix to the string (string -> string)
		rmprefix
			removes a prefix if present (string -> string)
		regex
			Replaces the string matched by the supplied regex with its first capture group (string -> string)
		last
			splits the string and returns last element (string -> string)
* Steps that work for single elements and return a single element:
		follow
			follows the specified link and returns the root node of the resulting document (string -> node)
* Steps that work for single elements and split them into a list:
		split
			splits the string (string -> stringlist)
		xpathls
			follows the xpath down the tree, returns all elements (node -> nodelist or stringlist)
* Steps that work for lists and merge them back into a single element:
		pick
			picks the n-th element from the list (nodelist -> node, stringlist -> string)
		combine
			combines all strings of the list (stringlist -> string)

Scraping feeds
^^^^^^^^^^^^^^^^^^^^^

:meth:`parse_all` is a function to scrape any well-structured feed of regular
elements. Since its arguments may be confusing, let's look at a simple example.
Say we want to scrape all locations of a website that shows 3 entries per page
and its URLs look like this:

	https://coolplaces.tld/top?start=0
	https://coolplaces.tld/top?start=3
	https://coolplaces.tld/top?start=6
	etc...

We would then supply ``base_url="https://bestgallery.tld/newest?start={page}"``,
``start_page=0`` and ``page_multiplier=3`` (since Page 0 needs a
0, page 1 needs a 3 and so on).

If our page has a weird URL logic, we can simply supply a function instead that
takes the logical page number (0, 1, 2, ...) as input and returns the string that
should be inserted into the URL.

Now let's have a look at the relevant part of our webpage:

.. code-block:: html

	<body>
		<div id="cards_area">
			<div class="place_box" id="place_box_rivendell">
				<div style="background-image('/rivendell.png');"></div>
				<h3 class="place_name">Rivendell</h3>
				<span class="place_leader">Leader: Elrond</span>
			</div>
			<div class="place_box" id="place_box_gondolin">
				<div style="background-image('/tumladen_vale.jpg');"></div>
				<h3 class="place_name">Gondolin</h3>
				<span class="place_leader">Leader: Turgon</span>
			</div>
			<div class="place_box" id="place_box_holymountain">
				<div style="background-image('/oiolosse.png');"></div>
				<h3 class="place_name">Taniquetil</h3>
				<span class="place_leader">Leader: Manwë</span>
			</div>
		</div>
	</body>

As ``steps_elements`` we need to supply the steps to acquire a list of elements - simple enough:


.. code-block:: json

	[
		{"type":"xpath","instruction":"//div[@id='cards_area']//div[@class='place_box']"}
	]

Now, we want to return several pieces of information from each element. As ``steps_content``, we pass:

.. code-block:: json

	{
		"identifier":[
			{"type":"xpath","instruction":"./@id"},
			{"type":"rmprefix","instruction":"place_box_"}
		],
		"image_url":[
			{"type":"xpath","instruction":"./div/@style"},
			{"type":"regex","instruction":"background-image('(.*)');"}
		],
		"name":[
			{"type":"xpath","instruction":"./h3/text()"}
		],
		"leader":[
			{"type":"xpath","instruction":"./span/text()"},
			{"type":"regex","instruction":"Leader: (.*)"}
		]
	}

This will iterate through all places and save the according values in a dictionary:

.. code-block:: python

	[
		{
			"identifier": "rivendell",
			"image_url": "rivendell.png",
			"name": "Rivendell",
			"leader": "Elrond"
		},
		{
			"identifier": "gondolin",
			"image_url": "tumladen_vale.jpg",
			"name": "Gondolin",
			"leader": "Turgon"
		},
		{
			"identifier": "holymountain",
			"image_url": "oiolosse.png",
			"name": "Taniquetil",
			"leader": "Manwë"
		},
	]


If we pass the argument ``stop=42``, the parsing will stop after we have found 42
arguments. Alternatively (or additionally), we can pass as ``stopif`` the following:

.. code-block:: python

	{
		"leader":lambda x: x=="Morgoth" or x=="Sauron",
		"image_url":lambda x: x.endswith(".gif")
	}

This means that if we parse a place with the leader "Morgoth" or "Sauron", or if
we parse a place that has a .gif-image, we immediately stop parsing.


API Reference
---------------

.. automodule:: doreah.scraping
   :members:
