from polyforce import Config, polycheck


@polycheck(ignore=..., ignored_types=...)
def my_function() -> None:
    ...
