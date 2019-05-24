PyHP / Python Hypertext Processor
==================================

How To
---------------

PyHP Syntax
^^^^^^^^^^^^^^^^^^^^^

Any strict (XML-compliant) html document is a valid pyhp document. Server-side processing
can be achieved with the help of ``<pyhp>`` nodes. Their meaning is determined by their arguments.
Nodes without any arguments are code blocks: they may contain arbitrary python code. Indentation
can be chosen to match the position in the xml tree, but must then be consistent within the block.
The first and last line (those containing the ``<pyhp>`` and ``</pyhp>`` tags) must not contain code.

The following pyhp nodes are available

echo
	The supplied expression will be evaluated and returned as string

.. code-block:: html

	<pyhp echo="len(stuff)" />
if
	Everything within this node is only sent to the client if the condition evaluates to true

.. code-block:: html

		<pyhp if="me['rank'] == 1 or !me.isintouchwithreality()">I'm the best!</pyhp>
for loop
	Everything within this node will be evaluated for each element in the iterable / mapping

.. code-block:: html

		<pyhp for="city" in="patriarchs" separator=" | ">The current patriarch of <pyhp echo="city" /> is <pyhp echo="patriarchs['city']" />. </pyhp>
assignment
	Assigns to a variable

.. code-block:: html

		<pyhp save="complicated_db_call(somestuff)[len(somelist)]['info']['important']" as="importantinfo" />
include
	Includes another pyhp file at this location.

.. code-block:: html

		<pyhp include="sidebar.pyhp" />

You can also access variables inside arguments of regular html nodes with curly braces:


.. code-block:: html

	<a href="{site.url}"><pyhp echo="site.name" /></a>


API Reference
---------------

.. automodule:: doreah.pyhp
   :members:
