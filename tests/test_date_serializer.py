from datetime import date

from tinydb import TinyDB, where
from tinydb.storages import JSONStorage

from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateSerializer


def test_serializer(tmpdir):
    path = str(tmpdir.join('db.json'))

    serializer = SerializationMiddleware(JSONStorage)
    serializer.register_serializer(DateSerializer(), 'TinyDate')
    db = TinyDB(path, storage=serializer)

    date_ = date(2000, 1, 1)

    db.insert({'date': date_})
    db.insert({'int': 2})
    assert db.count(where('date') == date_) == 1
    assert db.count(where('int') == 2) == 1


def test_serializer_nondestructive(tmpdir):
    path = str(tmpdir.join('db.json'))

    serializer = SerializationMiddleware(JSONStorage)
    serializer.register_serializer(DateSerializer(), 'TinyDate')
    db = TinyDB(path, storage=serializer)

    data = {'date': date.today(), 'int': 3, 'list': []}
    data_before = dict(data)  # implicitly copy
    db.insert(data)
    assert data == data_before


def test_serializer_recursive(tmpdir):
    path = str(tmpdir.join('db.json'))

    serializer = SerializationMiddleware(JSONStorage)
    serializer.register_serializer(DateSerializer(), 'TinyDate')
    db = TinyDB(path, storage=serializer)

    date_ = date(2000, 1, 1)
    date_today = date.today()
    dates = [{'date': date_, 'hp': 100}, {'date': date_today, 'hp': 1}]
    data = {'dates': dates, 'int': 10}
    db.insert(data)
    db.insert({'int': 2})
    assert db.count(where('dates').any(where('date') == date_)) == 1
    assert db.count(where('int') == 2) == 1
