# PolyModel

This is the object used for all the classes that want to enforce the static typing all over
the object itself.

This object is different from the [decorator](./decorator.md) as you don't need to specify
which functions should be enforced.

## How to use it

When using the `PolyModel` you must import it first.

```python
from polyforce import PolyModel
```

Once it is imported you can simply subclass it in your objects. Something like this:

```python hl_lines="5 8"
{!> ../docs_src/model/example.py !}
```

When adding the `PolyModel` object, will enable the static type checking to happen all over the
functions declared in the object.

### Ignore the checks

Well, there is not too much benefit of using `PolyModel` if you want to ignore the checks, correct?
Well, yes but you still can do it if you want.

There might be some scenarios where you want to override some checks and ignore the checks.

For this, **Polyforce** uses the [Config](./config.md) dictionary.

You simply need to pass `ignore=True` and the static type checking will be disabled for the class.

It will look like this:

```python hl_lines="9"
{!> ../docs_src/model/disable.py !}
```

### Ignore specific types

What if you want to simply ignore some types? Meaning, you might want to pass arbitraty values that
you don't want them to be static checked.

```python hl_lines="3 10 24"
{!> ../docs_src/model/ignored_types.py !}
```

This will make sure that the type `Actor` is actually ignore and assumed as type `Any` which also means
you can pass whatever value you desire since the type `Actor` is no longer checked.


### Integrations

**Polyforce** works also really well with integrations, for instance with [Pydantic](https://pydantic.dev).

The only thing you need to do is to import the [decorator](./decorator.md) and use it inside the
functions you want to enforce.

```python hl_lines="5 18 22"
{!> ../docs_src/model/integrations.py !}
```

This way you can use your favourite libraries with **Polyforce**.
