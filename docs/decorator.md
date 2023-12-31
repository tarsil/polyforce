# Decorator

**Polyforce** is quite versatile and for different tastes. You can use the [PolyModel](./model.md)
for you own objects or you can simply use the `polycheck` decorator for everything else.

## polycheck

This is the decorator that helps you with everything you need without the need of using an inherited
object.

The same parameters of the `PolyModel` are also allowed within the `polycheck`.

## How to use it

When using the `polycheck` you must import it first.

```python
from polyforce import polycheck
```

Once it is imported you can simply subclass it in your objects. Something like this:

```python hl_lines="5 19 26 32 40"
{!> ../docs_src/decorator/example.py !}
```

When adding the `polycheck` object, will enable the static type checking to happen all over the
functions declared.

### Ignore the checks

Well, there is not too much benefit of using `polycheck` if you want to ignore the checks, correct?
Well, yes but you still can do it if you want.

There might be some scenarios where you want to override some checks and ignore the checks.

For this, **Polyforce** uses the [Config](./config.md) dictionary.

You simply need to pass `ignore=True` and the static type checking will be disabled for the class.

It will look like this:

```python hl_lines="19 26"
{!> ../docs_src/decorator/disable.py !}
```

!!! Tip
    The decorator has the same fields as the `PolyModel` but since `polycheck` is done
    on a function basis, applying `ignore+True` **is the same as not adding the decorator at all**.
    This serves as example for documentation purposes only.

### Ignore specific types

What if you want to simply ignore some types? Meaning, you might want to pass arbitrary values that
you don't want them to be static checked.

```python hl_lines="3 22"
{!> ../docs_src/decorator/ignored_types.py !}
```

This will make sure that the type `Actor` is actually ignore and assumed as type `Any` which also means
you can pass whatever value you desire since the type `Actor` is no longer checked.

### Integrations

**Polyforce** works also really well with integrations, for instance with [Pydantic](https://pydantic.dev).

The only thing you need to do is to import the [decorator](./decorator.md) and use it inside the
functions you want to enforce.

This example is exactly the same as the one for [PolyModel](./model.md#integrations).

```python hl_lines="5 18 22"
{!> ../docs_src/model/integrations.py !}
```

This way you can use your favourite libraries with **Polyforce**.
