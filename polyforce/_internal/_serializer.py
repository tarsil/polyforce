from typing import Any

import orjson


def json_serializable(obj: Any) -> Any:
    """
    Serializes any object to a json like format.
    """
    serializer = orjson.dumps(obj, default=lambda o: o.__dict__)
    return orjson.loads(serializer)
