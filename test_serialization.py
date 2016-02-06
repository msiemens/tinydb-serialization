from datetime import datetime

from tinydb import TinyDB, where
from tinydb.storages import JSONStorage
from tinydb_serialization import Serializer, SerializationMiddleware


class DateTimeSerializer(Serializer):
    OBJ_CLASS = datetime
    FORMAT = '%Y-%m-%dT%H:%M:%S'

    def encode(self, obj):
        return obj.strftime(self.FORMAT)

    def decode(self, s):
        return datetime.strptime(s, self.FORMAT)


def test_serializer(tmpdir):
    path = str(tmpdir.join('db.json'))

    serializer = SerializationMiddleware(JSONStorage)
    serializer.register_serializer(DateTimeSerializer(), 'TinyDate')
    db = TinyDB(path, storage=serializer)

    date = datetime(2000, 1, 1, 12, 0, 0)

    db.insert({'date': date})
    db.insert({'int': 2})
    assert db.count(where('date') == date) == 1
    assert db.count(where('int') == 2) == 1


def test_serializer_nondestructive(tmpdir):
    path = str(tmpdir.join('db.json'))

    serializer = SerializationMiddleware(JSONStorage)
    serializer.register_serializer(DateTimeSerializer(), 'TinyDate')
    db = TinyDB(path, storage=serializer)

    data = {'date': datetime.utcnow(), 'int': 3}
    data_before = dict(data)  # implicitly copy
    db.insert(data)
    assert data == data_before

def test_serializer_recursive(tmpdir):
    path = str(tmpdir.join('db.json'))

    serializer = SerializationMiddleware(JSONStorage)
    serializer.register_serializer(DateTimeSerializer(), 'TinyDate')
    db = TinyDB(path, storage=serializer)

    date = datetime(2000, 1, 1, 12, 0, 0)
    datenow = datetime.utcnow()
    dates = [{"date":date,"hp":100}, {"date":datenow,"hp":1}]
    data = {"dates":dates, "int":10}
    db.insert(data)
    db.insert({'int': 2})
    assert db.count(where('dates') == date) == 1
    assert db.count(where('int') == 2) == 1
    assert db.get(where('int')==10).["dates"] == dates
    
