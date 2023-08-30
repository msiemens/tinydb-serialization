from datetime import date, datetime

from tinydb_serialization import Serializer


class DateTimeSerializer(Serializer):
    OBJ_CLASS = datetime  # The class this serializer handles

    def encode(self, obj):
        return obj.isoformat()

    def decode(self, s):
        return datetime.fromisoformat(s)


class DateSerializer(Serializer):
    OBJ_CLASS = date  # The class this serializer handles

    def encode(self, obj):
        return obj.isoformat()

    def decode(self, s):
        return date.fromisoformat(s)
