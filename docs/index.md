# Polyforce

<p align="center">
  <a href="https://polyforce.tarsild.io"><img src="https://res.cloudinary.com/tarsild/image/upload/v1696959172/packages/polyforce/logo_pyynl9.png" alt='Polyforce'></a>
</p>

<p align="center">
    <em>🔥 Enforce static typing in your codebase at runtime 🔥</em>
</p>

<p align="center">
<a href="https://github.com/tarsil/polyforce/workflows/Test%20Suite/badge.svg?event=push&branch=main" target="_blank">
    <img src="https://github.com/tarsil/polyforce/workflows/Test%20Suite/badge.svg?event=push&branch=main" alt="Test Suite">
</a>

<a href="https://pypi.org/project/polyforce" target="_blank">
    <img src="https://img.shields.io/pypi/v/polyforce?color=%2334D058&label=pypi%20package" alt="Package version">
</a>

<a href="https://pypi.org/project/polyforce" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/polyforce.svg?color=%2334D058" alt="Supported Python versions">
</a>
</p>

---

**Documentation**: [https://polyforce.tarsild.io][polyforce] 📚

**Source Code**: [https://github.com/tarsil/polyforce](https://github.com/tarsil/polyforce)

---

## Motivation

During software development we face issues where we don't know what do pass as specific parameters
or even return of the functions itself.

Tools like [mypy][mypy] for example, allow you to run static checking in your code and therefore
allowing to type your codebase properly but **it does not enforce it when running**.

For those coming from hevily static typed languages like **Java**, **.net** and many others, Python
can be overwhelming and sometimes confusing because of its versatility.

**Polyforce** was created to make sure you:

* Don't forget to type your functions and variables.
* Validates the typing in **runtime**.
* Don't forget thr return annotations.

Wouldn't be cool to have something like this:

> What if my function that expects a parameter of type string, if something else is passed could
simply fail, as intended?

This is where **Polyforce enters**.

## The library

Polyforce was designed to enforce the static typing **everywhere** in your code base. From functions
to parameters.

It was also designed to make sure the typing is enforced at runtime.

In other words, if you declare a type `string` and decide to pass an `integer`, it will blow throw
and intended error.

The library offers two ways of implementing the solution.

* [Via model](./model.md)
* [Via decorator](./decorator.md)

## How to use it

Let us see some scenarios where the conventional python is applied and then where **Polyforce**
can make the whole difference for you.

### Conventional Python

Let us start with a simple python function.

#### Simple function

```python
def my_function(name: str):
    return name
```

In the normal python world, this wouldn't make any difference, and let us be honest, if you don't care
about mypy or any related tools, this will work without any issues.

This will also allow this to run without any errors:

```python
my_function("Polyfactory") # returns "Polyfactory"
my_function(1) # returns 1
my_function(2.0) # returns 2.0
```

The example above is 100% valid for that specific function and all values passed will be returned
equaly valid and the reson for this is because Python **does not enforce the static typing** so
the `str` declared for the parameter `name` **is merely visual**.

#### With objects

```python
class MyClass:

    def my_function(name: str):
        return name
```

And then this will be also valid.

```python
my_class = MyClass()

my_class.my_function("Polyfactory") # returns "Polyfactory"
my_class.my_function(1) # returns 1
my_class.my_function(2.0) # returns 2.0
```

I believe you understand the gist of what is being referred here. So, what if there was a solution
where we actually enforce the typing at runtime? Throw some errors when something is missing from
the typing and also when the wrong type is being sent into a function?

Enters [Polyforce](#polyforce)

### Polyforce

Now, let us use the same examples used before but using **Polyforce** and see what happens?

#### Simple function

```python hl_lines="1"
from polyforce import polycheck


@polycheck
def my_function(name: str):
    return name
```

The example above it will throw a `ReturnSignatureMissing` or a `MissingAnnotation`
because the **missing return annotation** of the function or a parameter annotation respectively.

```python
my_function("Polyforce") # Throws an exception
```

The correct way would be:

```python hl_lines="1 5"
from polyforce import polycheck


@polycheck
def my_function(name: str) -> str:
    return name
```

So what if now you pass a value that is not of type string?

```python
my_function(1) # Throws an exception
```

This will also throw a `TypeError` exception because you are trying to pass a type `int` into a
declared type `str`.

#### With objects

The same level of validations are applied within class objects too.

```python hl_lines="1 4"
from polyforce import PolyModel


class MyClass(PolyModel):

    def __init__(self, name, age: int):
        ...

    def my_function(self, name: str):
        return name
```

The example above it will throw a `ReturnSignatureMissing` and a `MissingAnnotation`
because the **missing return annotation for both __init__ and the function** as well as the missing
types for the parameters in both.

The correct way would be:

```python hl_lines="1 4"
from polyforce import PolyModel


class MyClass(PolyModel):

    def __init__(self, name: str, age: int) -> None:
        ...

    def my_function(self, name: str) -> str:
        return name
```

## The Polyforce

As you can see, utilising the library is very simple and very easy, in fact, it was never so easy to
enforce statuc typing in python.

For classes, you simply need to import the `PolyModel`.

```python
from polyforce import PolyModel
```

And to use the decorator you simply can:

```python
from polyforce import polycheck
```

## PolyModel vs polycheck

When using `PolyModel`, there is no need to apply the `polycheck` decorator. The `PolyModel` is
smart enough to apply the same level of validations as the `polycheck`.

When using the `PolyModel` you can use normal python as you would normally do and that means
`classmethod`, `staticmethod` and normal functions.

This like this, the `polycheck` is used for all the functions that are not inside a class.

## Limitations

For now, **Polyforce** is not looking at **native magic methods** (usually start and end with double underscore).
In the future it is planned to understand those on a class level.

[polyforce]: https://polyforce.tarsild.io
[mypy]: https://mypy.readthedocs.io/en/stable/
