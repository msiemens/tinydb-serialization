tinydb-serialization
^^^^^^^^^^^^^^^^^^^^

|Build Status| |Coverage| |Version|

``tinydb-serialization`` provides serialization for objects that TinyDB
otherwise couldn't handle.

Usage
*****

Creating a Serializer
---------------------

In this example we implement a serializer for ``datetime`` objects:

.. code-block:: python

    from datetime import datetime
    from tinydb_serialization import Serializer

    class DateTimeSerializer(Serializer):
        OBJ_CLASS = datetime  # The class this serializer handles

        def encode(self, obj):
            return obj.strftime('%Y-%m-%dT%H:%M:%S')

        def decode(self, s):
            return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')

Using a Serializer
------------------

You can use your serializer like this:

.. code-block:: python

    >>> from tinydb.storages import JSONStorage
    >>> from tinydb_serialization import SerializationMiddleware
    >>>
    >>> serialization = SerializationMiddleware()
    >>> serialization.register_serializer(DateTimeSerializer(), 'TinyDate')
    >>>
    >>> db = TinyDB('db.json', storage=serialization)
    >>> db.insert({'date': datetime(2000, 1, 1, 12, 0, 0)})
    >>> db.all()
    [{'date': datetime.datetime(2000, 1, 1, 12, 0)}]

Changelog
*********

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

.. |Build Status| image:: http://img.shields.io/travis/msiemens/tinydb-serialization.svg?style=flat-square
   :target: https://travis-ci.org/msiemens/tinydb-serialization
.. |Coverage| image:: http://img.shields.io/coveralls/msiemens/tinydb-serialization.svg?style=flat-square
   :target: https://coveralls.io/r/msiemens/tinydb-serialization
.. |Version| image:: http://img.shields.io/pypi/v/tinydb-serialization.svg?style=flat-square
   :target: https://pypi.python.org/pypi/tinydb-serialization/
