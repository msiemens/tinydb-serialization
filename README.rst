tinydb-serialization
^^^^^^^^^^^^^^^^^^^^

|Build Status| |Coverage| |Version|

``tinydb-serialization`` provides serialization for objects that TinyDB
otherwise couldn't handle.

Usage
*****

General Usage
-------------

To use a serializer, create a ``SerializationMiddleware`` instance with
the storage class you want to use and register the serializers you want
to use. Then you pass the middleware instance as the storage to TinyDB:

.. code-block:: python

    >>> from tinydb import TinyDB, Query
    >>> from tinydb_serialization import SerializationMiddleware
    >>> from tinydb_serialization.serializers import DateTimeSerializer
    >>>
    >>> from datetime import datetime
    >>>
    >>> serialization = SerializationMiddleware(JSONStorage)
    >>> serialization.register_serializer(DateTimeSerializer(), 'TinyDate')
    >>>
    >>> db = TinyDB('db.json', storage=serialization)
    >>> db.insert({'date': datetime(2000, 1, 1, 12, 0, 0)})
    >>> db.all()
    [{'date': datetime.datetime(2000, 1, 1, 12, 0)}]
    >>> query = Query()
    >>> db.insert({'date': datetime(2010, 1, 1, 12, 0, 0)})
    >>> db.search(query.date > datetime(2005, 1, 1))
    [{'date': datetime.datetime(2010, 1, 1, 12, 0)}]

Provided Serializers
--------------------

- ``tinydb_serialization.serializers.DateTimeSerializer``: serializes ``datetime`` objects
  as ISO 8601 formatted strings

Creating Custom Serializers
---------------------------

In this example we implement a serializer for ``datetime`` objects (like the one provided
by this package):

.. code-block:: python

    from datetime import datetime
    from tinydb_serialization import Serializer

    class DateTimeSerializer(Serializer):
        OBJ_CLASS = datetime  # The class this serializer handles

        def encode(self, obj):
            return obj.isoformat()

        def decode(self, s):
            return datetime.fromisoformat(s)


Changelog
*********

**v2.1.0** (2021-01-23)
-----------------------

- Include the ``DateTimeSerializer`` in this package (see `issue #10 <https://github.com/msiemens/tinydb-serialization/pull/10>`_)
- Drop Python 3.6 support (as 3.7 is needed for date parsing)

**v2.0.0** (2020-05-26)
-----------------------

- Add TinyDB v4.0.0 support (see `pull request #9 <https://github.com/msiemens/tinydb-serialization/pull/9>`_)

**v1.0.4** (2017-03-27)
-----------------------

- Don't modify the original element if it contains a list (see
  `pull request #5 <https://github.com/msiemens/tinydb-serialization/pull/5>`_)

**v1.0.3** (2016-02-11)
-----------------------

- Handle nested data (nested dicts, lists) properly when serializing/deserializing (see
  `pull request #3 <https://github.com/msiemens/tinydb-serialization/pull/3>`_)

**v1.0.2** (2016-01-04)
-----------------------

- Don't destroy original data when serializing (see
  `pull request #2 <https://github.com/msiemens/tinydb-serialization/pull/2>`_)

**v1.0.1** (2015-11-17)
-----------------------

- Fix installation via pip (see `issue #1 <https://github.com/msiemens/tinydb-serialization/issues/1>`_)

**v1.0.0** (2015-09-27)
-----------------------

- Initial release on PyPI

.. |Build Status| image:: https://img.shields.io/github/workflow/status/msiemens/tinydb-serialization/Python%20CI?style=flat-square
   :target: https://github.com/msiemens/tinydb-serialization/actions?query=workflow%3A%22Python+CI%22
.. |Coverage| image:: https://img.shields.io/coveralls/msiemens/tinydb-serialization.svg?style=flat-square
   :target: https://coveralls.io/r/msiemens/tinydb-serialization
.. |Version| image:: https://img.shields.io/pypi/v/tinydb-serialization.svg?style=flat-square
   :target: https://pypi.python.org/pypi/tinydb-serialization/
