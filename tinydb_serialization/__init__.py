from abc import ABCMeta, abstractmethod, abstractproperty
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

        if data is None:
            return None

        for serializer_name in self._serializers:
            serializer = self._serializers[serializer_name]
            tag = '{{{0}}}:'.format(serializer_name)  # E.g: '{TinyDate}:'

            for table_name in data:
                table = data[table_name]

                for eid in table:
                    item = data[table_name][eid]

                    for field in item:
                        try:
                            if item[field].startswith(tag):
                                encoded = item[field][len(tag):]
                                item[field] = serializer.decode(encoded)
                        except AttributeError:
                            pass  # Not a string

        return data

    def write(self, data):
        for serializer_name in self._serializers:
            # If no serializers are registered, this code will just look up
            # the serializer list and continue. But if there are serializers,
            # the inner loop will run very often.
            # For that reason, the lookup of the serialized class is pulled
            # out into the outer loop:

            serializer = self._serializers[serializer_name]
            serializer_class = serializer.OBJ_CLASS

            for table_name in data:
                table = data[table_name]

                for eid in table:
                    item = data[table_name][eid]

                    for field in item:
                        if isinstance(item[field], serializer_class):
                            encoded = serializer.encode(item[field])
                            tagged = '{{{0}}}:{1}'.format(serializer_name,
                                                          encoded)

                            item[field] = tagged

        self.storage.write(data)
