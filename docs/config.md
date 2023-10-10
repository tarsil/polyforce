# Config

This is the object used for [PolyModel](./model.md) configuration options and only contains
a very little amount of paramenters.

## How to import

Very easy to import.

```python
from polyforce import Config
```

## How to use

The `Config` object is used inside objects that inherit from [PolyModel](./model.md).

```python
{!> ../docs_src/config.py !}
```

The same parameters of the config are also present in [polycheck](./decorator.md) decorator as well.

```python
{!> ../docs_src/decorator.py !}
```

## Parameters

* **ignore** - Flag indicating if the static type checking should be ignored. When this is applied
on a `PolyModel` level, **it will disable the checks for the whole class**, whereas when applied
on a `polycheck` level, it will only disable for the function where the decorator is being applied.

    <sup>Default: `False`</sup>

* **ignored_types** - List or tuple of python types, **any type** that should be ignored from the
static type checking. When a type is passed to `ignored_types=(...,)`, the attribute with declared
with the type being ignored will be assumed as `Any`.

    <sup>Default: `()`</sup>
