from datetime import datetime

from tinydb_serialization import Serializer


class DateTimeSerializer(Serializer):
    OBJ_CLASS = datetime  # The class this serializer handles

    def encode(self, obj):
        return obj.isoformat()

    def decode(self, s):
        return datetime.fromisoformat(s)
