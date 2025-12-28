# Pydantus
Pydantus: A builder framework for Pydantic

# Overview
This library allows you to use (almost) any pydantic model in a builder pattern.
It does this by implementing builder semantics and uses inspection to determine
which field to build. Validates is delayed until the .build() method is called

# Examples

## Basic Example
We can demonstrate the basic builder pattern of returning self and delaying
validation until the final build step.

```python
from pydantic import BaseModel
import pydantus

class MyModel(BaseModel):
    a_str: str
    a_num: float
    many_nums: list[int]


builder = pydantus.BuilderFrom(MyModel)

my_model = (builder
    .set_a_str('foo')
    .set_a_num(3.14)
    .set_many_nums([1, 2])
    .add_many_nums(3)
)

assert my_model.model_dump() == {
    'a_str': 'foo',
    'a_num': 3.14
    'many_nums': [1, 2, 3],
}
```

## Nested builders

We also can use nested builders in a fairly easy way. The nested model
can be turned into a BuilderFrom using the `.build_from_<sub_model>()`
syntax

```python
from pydantic import BaseModel
import pydantus

class NestedModel(BaseModel):
    a_num: float

class MyModel(BaseModel):
    a_str: str
    nested_model: NestedModel

builder = pydantus.BuilderFrom(MyModel)

builder.set_a_str('foo')
sub_builder = builder.build_from_nested_model()
sub_builder.set_a_num(3.14)

my_model = builder.build()

assert my_model.model_dump() == {
    'a_str': 'foo',
    'nested_model': {'a_num': 3.14}
}
```

You can also .set a builder explicitly

```python
...
sub_builder = pydantus.BuilderFrom(NestedModel)
builder.set_nested_model(sub_builder)
sub_builder.set_a_num(3.14)
...
```


When we have a list of nested models, this can be used to add
multiple builders that will all be resolved at build time.

```python
class MyModel(BaseModel):
    nested_models: list[NestedModel]


sub_builder = pydantus.BuilderFrom(NestedModel)
sub_builder.set_a_num(3.14)

builder = pydantus.BuilderFrom(MyModel).add_nested_models(sub_builder)
```
