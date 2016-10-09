Feature Hunter
====

A python module for trawling music websites that detects changes in lists of feature albums and sends notifications by email

Installation
====

Clone this repository

.. code:: bash
      git clone https://github.com/derwentx/feature-hunter

install the python package

.. code:: bash
      python setup.py install

play with some databases (an example databse is provided)

.. code:: bash
      cp /example_db.json ~
      cd ~
      python -m feature_hunter --db example_db.json

Roadmap
====
[x] Correctly identify changes in targets specified in database
[ ] Interface to easily add targets to database
[ ] Send alerts when changes are detected
