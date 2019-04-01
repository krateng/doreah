.. doreah documentation master file, created by
   sphinx-quickstart on Sun Mar 31 13:33:56 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Overview
==================================

Doreah is a useful little toolkit that offers shortcuts and abstractions for common operations.


Installing
-------------

Install doreah with the simple command ``pip install doreah``.


Configuration
--------------

Each module can be configured with a call to the function config(). However, it is recommended to use a ``.doreah`` configuration file in your project's directory. This way, the correct configuration will be used from the first import.

The .doreah file follows a simple key-value-format where the key is comprised of the module name, a dot and the configuration parameter, e.g.::

	logging.verbosity = 2



..
	Indices and tables
	==================

	* :ref:`genindex`
	* :ref:`modindex`
	* :ref:`search`
