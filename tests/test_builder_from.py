"""Tests for the Pydantus builder pattern."""

import pytest
from pydantic import BaseModel

import pydantus


class MyModel(BaseModel):
    """Example model from README."""

    a_str: str
    a_num: float
    many_nums: list[int]


class NestedModel(BaseModel):
    """A simple nested model."""

    a_num: float


class ParentModel(BaseModel):
    """A model containing a nested model."""

    a_str: str
    nested_model: NestedModel


class DeeplyNestedModel(BaseModel):
    """A model for deep nesting tests."""

    value: int


class MiddleModel(BaseModel):
    """A middle-level model containing a deeply nested model."""

    name: str
    deep: DeeplyNestedModel


class OuterModel(BaseModel):
    """An outer model for testing multi-level nesting."""

    title: str
    middle: MiddleModel


class ModelWithNestedList(BaseModel):
    """A model containing a list of nested models."""

    nested_models: list[NestedModel]


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


class TestNestedBuilders:
    """Tests for nested builder functionality."""

    def test_basic_nested_builder(self):
        """Test the nested builder pattern from README example."""
        builder = pydantus.BuilderFrom(ParentModel)

        builder.set_a_str("foo")
        sub_builder = builder.build_from_nested_model()
        sub_builder.set_a_num(3.14)

        my_model = builder.build()

        assert my_model.model_dump() == {
            "a_str": "foo",
            "nested_model": {"a_num": 3.14},
        }

    def test_nested_builder_returns_builder_instance(self):
        """Test that build_from_* returns a BuilderFrom instance."""
        builder = pydantus.BuilderFrom(ParentModel)
        sub_builder = builder.build_from_nested_model()

        assert isinstance(sub_builder, pydantus.BuilderFrom)

    def test_nested_builder_method_chaining(self):
        """Test that nested builders support method chaining."""
        builder = pydantus.BuilderFrom(ParentModel)

        sub_builder = builder.build_from_nested_model()
        result = sub_builder.set_a_num(1.0)

        assert result is sub_builder

    def test_nested_builder_with_chained_parent(self):
        """Test nested builder works with chained parent setters."""
        builder = pydantus.BuilderFrom(ParentModel)

        builder.set_a_str("chained")
        builder.build_from_nested_model().set_a_num(2.71)

        model = builder.build()

        assert model.a_str == "chained"
        assert model.nested_model.a_num == 2.71

    def test_deeply_nested_builders(self):
        """Test multi-level nested builders."""
        builder = pydantus.BuilderFrom(OuterModel)

        builder.set_title("outer")
        middle_builder = builder.build_from_middle()
        middle_builder.set_name("middle")
        deep_builder = middle_builder.build_from_deep()
        deep_builder.set_value(42)

        model = builder.build()

        assert model.model_dump() == {
            "title": "outer",
            "middle": {
                "name": "middle",
                "deep": {"value": 42},
            },
        }

    def test_nested_model_set_directly(self):
        """Test that nested models can still be set directly with set_*."""
        builder = pydantus.BuilderFrom(ParentModel)

        builder.set_a_str("direct")
        builder.set_nested_model(NestedModel(a_num=99.9))

        model = builder.build()

        assert model.nested_model.a_num == 99.9

    def test_nested_builder_overrides_direct_set(self):
        """Test that using build_from after set_ overrides the value."""
        builder = pydantus.BuilderFrom(ParentModel)

        builder.set_a_str("test")
        builder.set_nested_model(NestedModel(a_num=1.0))
        # Now use build_from which should override
        builder.build_from_nested_model().set_a_num(2.0)

        model = builder.build()

        assert model.nested_model.a_num == 2.0

    def test_set_builder_explicitly(self):
        """Test setting a builder explicitly via set_*."""
        sub_builder = pydantus.BuilderFrom(NestedModel)
        sub_builder.set_a_num(3.14)

        builder = pydantus.BuilderFrom(ParentModel)
        builder.set_a_str("foo")
        builder.set_nested_model(sub_builder)

        model = builder.build()

        assert model.model_dump() == {
            "a_str": "foo",
            "nested_model": {"a_num": 3.14},
        }

    def test_add_builders_to_list(self):
        """Test adding builders to a list field."""
        sub_builder1 = pydantus.BuilderFrom(NestedModel)
        sub_builder1.set_a_num(1.0)

        sub_builder2 = pydantus.BuilderFrom(NestedModel)
        sub_builder2.set_a_num(2.0)

        builder = pydantus.BuilderFrom(ModelWithNestedList)
        builder.add_nested_models(sub_builder1)
        builder.add_nested_models(sub_builder2)

        model = builder.build()

        assert model.model_dump() == {
            "nested_models": [{"a_num": 1.0}, {"a_num": 2.0}],
        }

    def test_mix_builders_and_models_in_list(self):
        """Test mixing builders and actual models in a list field."""
        sub_builder = pydantus.BuilderFrom(NestedModel)
        sub_builder.set_a_num(1.0)

        builder = pydantus.BuilderFrom(ModelWithNestedList)
        builder.add_nested_models(sub_builder)
        builder.add_nested_models(NestedModel(a_num=2.0))

        model = builder.build()

        assert model.model_dump() == {
            "nested_models": [{"a_num": 1.0}, {"a_num": 2.0}],
        }


class TestBuilderTemplateRejection:
    """Tests that BuilderTemplates cannot be set as field values."""

    def test_set_rejects_builder_template(self):
        """Test that set_* rejects BuilderTemplate values."""
        template = pydantus.BuilderFrom(NestedModel).partial()
        builder = pydantus.BuilderFrom(ParentModel)

        with pytest.raises(pydantus.BuilderTemplateValueError) as exc_info:
            builder.set_nested_model(template)

        assert "Cannot set a BuilderTemplate" in str(exc_info.value)
        assert "nested_model" in str(exc_info.value)
        assert ".new()" in str(exc_info.value)

    def test_add_rejects_builder_template(self):
        """Test that add_* rejects BuilderTemplate values."""
        template = pydantus.BuilderFrom(NestedModel).partial()
        builder = pydantus.BuilderFrom(ModelWithNestedList)

        with pytest.raises(pydantus.BuilderTemplateValueError) as exc_info:
            builder.add_nested_models(template)

        assert "Cannot set a BuilderTemplate" in str(exc_info.value)
        assert "nested_models" in str(exc_info.value)

    def test_set_allows_builder_from(self):
        """Test that set_* still allows concrete BuilderFrom instances."""
        sub_builder = pydantus.BuilderFrom(NestedModel)
        sub_builder.set_a_num(3.14)

        builder = pydantus.BuilderFrom(ParentModel)
        builder.set_a_str("test")
        builder.set_nested_model(sub_builder)

        model = builder.build()

        assert model.nested_model.a_num == 3.14

    def test_add_allows_builder_from(self):
        """Test that add_* still allows concrete BuilderFrom instances."""
        sub_builder = pydantus.BuilderFrom(NestedModel)
        sub_builder.set_a_num(2.71)

        builder = pydantus.BuilderFrom(ModelWithNestedList)
        builder.add_nested_models(sub_builder)

        model = builder.build()

        assert model.nested_models[0].a_num == 2.71

    def test_set_allows_template_new(self):
        """Test that .new() on a template produces a usable builder."""
        template = pydantus.BuilderFrom(NestedModel).set_a_num(1.0).partial()

        builder = pydantus.BuilderFrom(ParentModel)
        builder.set_a_str("test")
        # Using .new() creates a concrete BuilderFrom, which is allowed
        builder.set_nested_model(template.new())

        model = builder.build()

        assert model.nested_model.a_num == 1.0

    def test_add_allows_template_new(self):
        """Test that .new() on a template works with add_*."""
        template = pydantus.BuilderFrom(NestedModel).set_a_num(5.0).partial()

        builder = pydantus.BuilderFrom(ModelWithNestedList)
        builder.add_nested_models(template.new())

        model = builder.build()

        assert model.nested_models[0].a_num == 5.0

    def test_nested_template_from_partial(self):
        """Test that partial() on a nested builder returns a template."""
        builder = pydantus.BuilderFrom(ParentModel)
        builder.set_a_str("test")

        # build_from returns a BuilderFrom, partial() returns a template
        nested_template = builder.build_from_nested_model().partial()

        # Trying to set this template should fail
        other_builder = pydantus.BuilderFrom(ParentModel)
        with pytest.raises(pydantus.BuilderTemplateValueError):
            other_builder.set_nested_model(nested_template)
