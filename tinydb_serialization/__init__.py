from abc import ABCMeta, abstractmethod, abstractproperty
from copy import deepcopy
from tinydb import TinyDB
from tinydb.middlewares import Middleware
from tinydb.utils import with_metaclass


class Serializer(with_metaclass(ABCMeta, object)):
    """
    The abstract base class for Serializers.
    Allows TinyDB to handle arbitrary objects by running them through a list
    of registerd serializers.
    Every serializer has to tell which class it can handle.
    """

    @abstractproperty
    def OBJ_CLASS(self):
        raise NotImplementedError('To be overriden!')

    @abstractmethod
    def encode(self, obj):
        """
        Encode an object.
        :param obj:
        :return:
        :rtype: str
        """
        raise NotImplementedError('To be overriden!')

    @abstractmethod
    def decode(self, s):
        """
        Decode an object.
        :param s:
        :type s: str
        :return:
        """
        raise NotImplementedError('To be overriden!')


def walk_if_do(d, predicate, action):
        if isinstance(d, dict):
            try:
                dd = d.iteritems()
            except AttributeError:
                dd = d.items()
        else:
            dd = enumerate(d)
        for k, v in dd:
            if predicate(v):
                action(d, k, v)
            elif isinstance(v, (dict, list, tuple)):
                walk_if_do(v, predicate, action)


class SerializerUtils(object):

    def __init__(self):
        self.serializer_name = ""
        self.serializer = None
        self.tag = ""
        self.OBJ_CLASS = None
        self.found = False

    def verify_string(self, s):
        try:
            if s.startswith(self.tag):
                return True
        except AttributeError:
            pass  # Not a string
        return False

    def decode_inplace(self, d, k, v):
        encoded = v[len(self.tag):]
        d[k] = self.serializer.decode(encoded)

    def verify_object(self, obj):
        return isinstance(obj, self.OBJ_CLASS)

    def encode_inplace(self, d,k,v):
        encoded = self.serializer.encode(v)
        tagged = '{{{0}}}:{1}'.format(
            self.serializer_name,
            encoded)
        d[k] = tagged

    def find(self,d,k,v):
        self.found = True


class SerializationMiddleware(Middleware):
    """
    Provide custom serialization for TinyDB.
    This middleware allows users of TinyDB to register custom serializations.
    The serialized data will be passed to the wrapped storage and data that
    is read from the storage will be deserialized.
    """

    def __init__(self, storage_cls=TinyDB.DEFAULT_STORAGE):
        super(SerializationMiddleware, self).__init__(storage_cls)

        self._serializers = {}

    def register_serializer(self, serializer, name):
        """
        Register a new Serializer.
        When reading from/writing to the underlying storage, TinyDB
        will run all objects through the list of registered serializers
        allowing each one to handle objects it recognizes.
        .. note:: The name has to be unique among this database instance.
                  Re-using the same name will overwrite the old serializer.
                  Also, registering a serializer will be reflected in all
                  tables when reading/writing them.
        :param serializer: an instance of the serializer
        :type serializer: tinydb.serialize.Serializer
        """
        self._serializers[name] = serializer

    def read(self):
        data = self.storage.read()
        utils = SerializerUtils()

        if data is None:
            return None

        for serializer_name in self._serializers:
            utils.serializer = self._serializers[serializer_name]
            utils.tag = '{{{0}}}:'.format(serializer_name) # E.g:'{TinyDate}:'

            for table_name in data:
                table = data[table_name]

                for eid in table:
                    item = data[table_name][eid]
                    walk_if_do(
                        item,
                        utils.verify_string,
                        utils.decode_inplace
                    )

        return data

    def write(self, data):
        # We only make a copy of the data if any serializer would overwrite
        # existing data.
        data_copied = False
        utils = SerializerUtils()
        for serializer_name in self._serializers:
            # If no serializers are registered, this code will just look up
            # the serializer list and continue. But if there are serializers,
            # the inner loop will run very often.
            # For that reason, the lookup of the serialized class is pulled
            # out into the outer loop:

            utils.serializer = self._serializers[serializer_name]
            utils.OBJ_CLASS = utils.serializer.OBJ_CLASS
            utils.serializer_name = serializer_name

            for table_name in data:
                table = data[table_name]

                for eid in table:
                    item = data[table_name][eid]
                    if not data_copied:
                        print("I'm here!")
                        utils.found = False
                        walk_if_do(item, utils.verify_object, utils.find)
                        if utils.found:
                            data = deepcopy(data)
                            data_copied = True
                            item = data[table_name][eid]
                            print("Made deepcopy")
                    walk_if_do(
                        item,
                        utils.verify_object,
                        utils.encode_inplace
                    )
        self.storage.write(data)

