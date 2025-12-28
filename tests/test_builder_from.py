"""Tests for the Pydantus builder pattern."""

from pydantic import BaseModel

import pydantus


class MyModel(BaseModel):
    """Example model from README."""

    a_str: str
    a_num: float
    many_nums: list[int]


class TestBuilderFrom:
    """Tests for Pydantus.BuilderFrom functionality."""

    def test_basic_builder_pattern(self):
        """Test the basic builder pattern from README example."""
        builder = pydantus.BuilderFrom(MyModel)

        my_model = (
            builder.set_a_str("foo")
            .set_a_num(3.14)
            .set_many_nums([1, 2])
            .add_many_nums(3)
            .build()
        )

        assert my_model.model_dump() == {
            "a_str": "foo",
            "a_num": 3.14,
            "many_nums": [1, 2, 3],
        }

    def test_set_string_field(self):
        """Test setting a string field."""
        builder = pydantus.BuilderFrom(MyModel)
        builder.set_a_str("hello")
        model = builder.set_a_num(1.0).set_many_nums([]).build()

        assert model.a_str == "hello"

    def test_set_numeric_field(self):
        """Test setting a numeric field."""
        builder = pydantus.BuilderFrom(MyModel)
        model = builder.set_a_str("x").set_a_num(42.5).set_many_nums([]).build()

        assert model.a_num == 42.5

    def test_set_list_field(self):
        """Test setting a list field."""
        builder = pydantus.BuilderFrom(MyModel)
        model = (
            builder.set_a_str("x").set_a_num(1.0).set_many_nums([10, 20, 30]).build()
        )

        assert model.many_nums == [10, 20, 30]

    def test_add_to_list_field(self):
        """Test adding individual items to a list field."""
        builder = pydantus.BuilderFrom(MyModel)
        model = (
            builder.set_a_str("x")
            .set_a_num(1.0)
            .set_many_nums([1])
            .add_many_nums(2)
            .add_many_nums(3)
            .build()
        )

        assert model.many_nums == [1, 2, 3]

    def test_method_chaining(self):
        """Test that all setter methods return the builder for chaining."""
        builder = pydantus.BuilderFrom(MyModel)

        result = builder.set_a_str("test")
        assert result is builder

        result = builder.set_a_num(1.0)
        assert result is builder

        result = builder.set_many_nums([])
        assert result is builder
