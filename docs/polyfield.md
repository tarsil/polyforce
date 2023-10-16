# PolyField

The **PolyField** took great inspiration from [Pydantic](https://pydantic.dev) in the way it is
generated.

Although being inspired from great tools, it acts in a unique fashion and it is what is internally
used for the validation of the static typing.

Why the **PolyField** then? Well, for structure of course. To make sure there is always a source
of truth when the Polyforce is taking action.

## The PolyField

To import the `PolyField` you only need to:

```python
from polyforce import PolyField
```

Or

```python
from polyforce.fields import PolyField
```

The `PolyField` should generally not be initialised directly, instead the [Field](#field) should be
used instead.

### Parameters

The PolyField has the following parameters:

* **annotation** - The annotation of the field being created/checked.
* **default** - The default value of the field.
* **factory** - The altenative to `default`, usually a callable.
* **name** - The name of the field.

    <sup>Default: Name of the attribute</sup>

* **title** - The title of the field.
* **description** - The description of the field.

!!! Warning
    `title` and `description` for now are used for documentation purposes only and
    **you can only pass or `default` or `factory` but not both**.

Let us see how a declaration of class using the Polyforce would look like internally and how the
polyfield plays the role here.

```python
{!> ../docs_src/polyfield/model.py !}
```

### How does it work

As you can see, you simply declare the Python object subclassing the [PolyModel][polymodel] and internally
the Polyforce will generate the polyfields for you.

The way of accessing the generated polyfields is as the following:

```python
user = User(name="Polyforce", email="polymodel@example.com")
user.poly_fields

{
    '__init__': {
        'name': PolyField(annotation=str, required=True, name='name'),
        'email': PolyField(annotation=str, required=True, name='email')},
    'set_name': {'name': PolyField(annotation=str, required=True, name='name')},
    'set_email': {'email': PolyField(annotation=str, required=True, name='email')}
}

```

Now, this is a lot to unwrap!

In a nutshell, the [PolyModel][polymodel] **does a lot of the heavy lifting for you**.

For each function of the object subclassing the [PolyModel][polymodel]. it will generate unique
polyfields for each declare function and then use them for the enforcing of the static typing.

As mentioned before, the [PolyField](#the-polyfield) should generally not be initialised directly and
instead, you can simply use the [Field](#field).

## Field

What is this `Field`? In a nutshell, it is your way of explicitly saying exactly what you want the
field to be, giving you more direct control of what is happening.

To import the `Field` you only need to:

```python
from polyforce import Field
```

Or

```python
from polyforce.fields import Field
```

### How does it work

In pratical terms, how does this `Field` actually work.

Let us see the same example as before and go from there.

```python
{!> ../docs_src/polyfield/model.py !}
```

Until here, everything is ok btu what is actually happening is that the [PolyModel][polymodel] will
generate the [polyfields](#the-polyfield) for you.

Now, what happens if we apply the `Field`, basically something like this:

```python
{!> ../docs_src/polyfield/field_simple.py !}
```

In the end, you are the one explicitly saying exactly what type of [PolyField](#the-polyfield) you
want to be generated and to access the results is exactly in the same way as before.

```python
user = User(name="Polyforce", email="polymodel@example.com")
user.poly_fields

{
    '__init__': {
        'name': PolyField(annotation=str, required=True, name='name'),
        'email': PolyField(annotation=str, required=True, name='email')},
    'set_name': {'name': PolyField(annotation=str, required=True, name='name')},
    'set_email': {'email': PolyField(annotation=str, required=True, name='email')}
}

```

### Required

When the [PolyModel][polymodel] generates the [PolyField](#polyfield), it will evaluate if the field
is required or not and the best way of making sure is to use the [Field](#field) and provide a `default`
value.

```python hl_lines="8"
{!> ../docs_src/polyfield/required.py !}
```

Let us see what is happening. In the `__init__`, the `name` has no `default` and therefore, **it is required**.

```python
user = User(name="Polyforce", email="polymodel@example.com")
user.poly_fields["__init__"]["name"]

# PolyField(annotation=str, required=True, name='name')
```

On the other hand, for the `set_name`, a `default="model"` is provided, which means, the field is
no longer required as it will default to `model` if nothing is provided.

```python
user = User(name="Polyforce", email="polymodel@example.com")
user.poly_fields["set_name"]["name"]

# PolyField(annotation=str, required=False, default='test', name='name')
```

### Available functions

Since the [Field](#field) generates [PolyField](#the-polyfield) on the fly, that also means you
also have access to some internal functions.

Let us continue with the following example.

```python
{!> ../docs_src/polyfield/required.py !}
```

#### is_required()

In practice, every `PolyField` has access to this.

```python hl_lines="4"
user = User(name="Polyforce", email="polymodel@example.com")
field = user.poly_fields["set_name"]["name"]

field.is_required() # False
```

#### get_default()

The way of getting the `default` value of the field.

```python hl_lines="4"
user = User(name="Polyforce", email="polymodel@example.com")
field = user.poly_fields["set_name"]["name"]

field.get_default() # "model"
```

[polymodel]: ./model.md
