# pydantus
Pydactus: A builder framework for Pydantic

# Overview
This library allows you to use (almost) any pydantic model in a builder pattern.
It does this by implementing builder semantics and uses inspection to determine
which field to build. Validates is delayed until the .build() method is called

# Examples

## Basic Example

```python
class MyModel(BaseModel):
    a_str: str
    a_num: float
    many_nums: list[int]


builder = Pydantus.BuilderFrom(MyModel)

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