from json import JSONEncoder
from typing import Any, List

import orjson


class SetEncoder(JSONEncoder):
    """
    Encoders for Set and set types, making sure
    the set are converted to lists upon encoding.
    """

    def default(self, obj: Any) -> List[Any]:
        return list(obj)


def json_serializable(obj: Any) -> Any:
    """
    Serializes any object to a json like format.
    """
    if isinstance(obj, set):
        obj = SetEncoder().encode(obj)

    serializer = orjson.dumps(obj, default=lambda o: o.__dict__)
    return orjson.loads(serializer)
