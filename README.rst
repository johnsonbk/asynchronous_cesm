Overview
========

This repository contains scripts to manage the asynchronous integration of a
CESM ensemble so that it can be used within a data assimilation cycle using
DART.

Database
--------

The state of the integration is recorded into a sqlite3 database that is named
``db.sqlite3``. The database contains two tables:

A. The first table is named ``experiment`` and it only has a single row that is
   updated as the experiment progresses. It contains the overall state of the 
   experiment and has five fields:

   1. ``id`` INTEGER NOT NULL PRIMARY KEY
   2. ``cycle`` INTEGER
   3. ``size`` INTEGER
   4. ``start_year`` INTEGER
   5. ``start_month`` INTEGER
   6. ``start_day`` INTEGER
   7. ``start_tod`` INTEGER
   8. ``resubmit`` INTEGER
   9. ``status`` TEXT

B. The second table is named ``cycles`` and it contains a row for each cycle 
   that the experiment has begun. It contains the state of each ensemble --
   for example, ``status_of_0003`` -- and also contains five additional fields
   that describe a particular cycle:

   1. ``cycle`` INTEGER NOT NULL PRIMARY KEY
   2. ``year`` INTEGER
   3. ``month`` INTEGER
   4. ``day`` INTEGER
   5. ``tod`` INTEGER

Helper files
------------

``ensemble.py``
~~~~~~~~~~~~~~~

In order to simplify the scripts, much of the configuration is stored in the
``ensemble.py`` file which contains three class definitions, which behave more
like namelists, structs or derived types.

In essence, they contain configuration information that is then inherited by
other classes. The child classes actually have methods that accomplish
meaningful tasks.

- ``Case``: contains the configuration of the experiment itself.
- ``Machine``: contains the configuration of the machine the experiment is
  being run on.
- ``Reference``: contains the configuration of the reference case that the 
  experiment uses for restart files.

``tools.py``
~~~~~~~~~~~~

The classes contained in ``tools.py`` actually have methods that do work. The 
classes are organized around specific topics.

- ``CIME``: Provides methods to check the status of a member case.
- ``Cron``: Contains methods to create and delete cron jobs.
- ``Database``: Contains methods to handle the sqlite queries needed to record
  and update the state of the ensemble and the experiment.
- ``Git``: Has methods to initialize a repository in the caseroot directories
  and run directories and handle the resets.
- ``Message``: Sends messages both to and from the user with a status update
  from the experiment.

Build files
-----------

``build_ensemble.py`` initiates construction of the initial ensemble. It is
responsible for doing three things:

1. Submitting submitting a batch job for each ensemble member that initiates
   the build of its case.
2. Creating the ``db.sqlite3`` database that stores the state of the experiment
   and the state of the ensemble.
3. Initiating a cron job that runs ``check_database.py`` every five minutes to
   check on the status of the build.

``build_single_case.py`` is submitted by ``build_ensemble.py`` and is
responsible for creating an individual CESM case. If a build completes, it 
updates the relevant ``status_of_XXXX`` field in the ``db.sqlite3`` database
to record that the member has completed building.

check_database file
-------------------

``check_database.py`` is called as a cron job every five minutes. It is responsible
for checking the ``db.sqlite3`` database to determine the status of the
experiment.

It first checks the ``experiment`` table in the database to see if the
experiment is one of nine statuses:

1. ``building``
2. ``failed building``
3. ``completed building``
4. ``assimilating``
5. ``failed assimilating``
6. ``completed assimilating``
7. ``integrating``
8. ``failed integrating``
9. ``completed integrating``

Based on the status of the experiment, it does one of two things:

1. It emails the user to inform them of the status of the experiment.
2. It calls the assimilate or integrate files to continue the experiment.

.. important::

   The check_database script only reads the ``db.sqlite3`` database file and
   either sends an email or calls the controller in order to prevent a race
   condition. It does not do any time-consuming tasks that may not be
   complete within the five minute interval before it gets called again as
   a cron job.

Assimilate file
---------------

``assimilate.py`` is responsible for checking to see if the experiment has
either ``completed building`` or  ``completed assimilating``.

If so, then assimilate will submit a job to begin an assimilation.

Integrate file
--------------

``integrate.py`` is responsible for checking to see if the experiment has
``completed assimilating``. 

If so, then integrate will submit a job to begin an integration.

Test-driven development
-----------------------

Since these codes are meant to be run asynchronously on a distributed computing system, it is
difficult to ensure whether they work as intended. Therefore a suite of comprehensive tests is
included with the code that can be used to help ensure the code still works as intended when it is
modified.

The test suite uses Python's standard `unittest <https://docs.python.org/3/library/unittest.html>`_
testing framework.

.. note::

   The syntax for Python's unittest library was originally borrowed from a different language so 
   it uses the `camelCase <https://en.wikipedia.org/wiki/Camel_case>`_ naming convention rather than
   instead of Python's typical use `snake_case <https://en.wikipedia.org/wiki/Snake_case>`_.
   
   For example the set up method is stylized as ``setUp`` instead of the using the ``set_up`` naming
   convention commonly used in python.

This suite of test scripts is included so it can run by users who alter the asyncrhonous code to
help ensure the modified code runs as intended. For an introduction to Python's unittest library,
watch `Corey Schafer's tutorial on YouTube <https://www.youtube.com/watch?v=6tNS--WetLI>`_.
