"""Tests for the immutable/template builder patterns."""

from pydantic import BaseModel

import pydantus
from pydantus.builder_template import BuilderTemplate


class Person(BaseModel):
    """Simple model for testing."""

    name: str
    parent: str


class NestedChild(BaseModel):
    """Nested model for testing."""

    value: int


class ParentWithNested(BaseModel):
    """Model with nested child for testing."""

    name: str
    child: NestedChild


class TestNew:
    """Tests for BuilderFrom.new() functionality."""

    def test_new_creates_independent_copy(self):
        """Test that new() creates a builder with separate data."""
        base = pydantus.BuilderFrom(Person)
        base.set_parent("Alice")

        copy = base.new()
        copy.set_name("Bob")

        # Original should not have the name set
        base.set_name("Carol")

        assert copy.build().name == "Bob"
        assert base.build().name == "Carol"

    def test_new_copies_existing_data(self):
        """Test that new() includes data already set on the builder."""
        base = pydantus.BuilderFrom(Person)
        base.set_parent("Alice").set_name("Original")

        copy = base.new()

        # Copy should have the parent from base
        copy.set_name("Changed")
        result = copy.build()

        assert result.parent == "Alice"
        assert result.name == "Changed"

    def test_new_deep_copies_nested_builders(self):
        """Test that nested builders are also copied."""
        base = pydantus.BuilderFrom(ParentWithNested)
        base.set_name("Parent")
        base.build_from_child().set_value(1)

        copy = base.new()
        copy.build_from_child().set_value(2)

        assert base.build().child.value == 1
        assert copy.build().child.value == 2

    def test_new_deep_copies_lists(self):
        """Test that list data is deep copied."""

        class ModelWithList(BaseModel):
            items: list[int]

        base = pydantus.BuilderFrom(ModelWithList)
        base.set_items([1, 2, 3])

        copy = base.new()
        copy.set_items([4, 5, 6])

        assert base.build().items == [1, 2, 3]
        assert copy.build().items == [4, 5, 6]


class TestPartial:
    """Tests for BuilderFrom.partial() functionality."""

    def test_partial_returns_template_builder(self):
        """Test that partial() returns a BuilderTemplate instance."""
        builder = pydantus.BuilderFrom(Person)
        template = builder.partial()

        assert isinstance(template, BuilderTemplate)

    def test_partial_spawns_copy_on_set(self):
        """Test that setting a field on partial spawns a new builder."""
        base = pydantus.BuilderFrom(Person).set_parent("Alice")
        template = base.partial()

        result = template.set_name("Bob")

        # Result should be a BuilderFrom, not a BuilderTemplate
        assert isinstance(result, pydantus.BuilderFrom)
        assert not isinstance(result, BuilderTemplate)

    def test_partial_allows_multiple_variations(self):
        """Test the main use case: creating multiple objects from a template."""
        children = pydantus.BuilderFrom(Person).set_parent("Alice").partial()

        child_a = children.set_name("Bob").build()
        child_b = children.set_name("Carol").build()

        assert child_a.model_dump() == {"name": "Bob", "parent": "Alice"}
        assert child_b.model_dump() == {"name": "Carol", "parent": "Alice"}

    def test_partial_build_spawns_copy(self):
        """Test that build() on a partial spawns a copy first."""
        base = pydantus.BuilderFrom(Person).set_parent("Alice").set_name("Bob")
        template = base.partial()

        result = template.build()

        assert result.name == "Bob"
        assert result.parent == "Alice"

    def test_partial_new_returns_concrete_builder(self):
        """Test that new() on a BuilderTemplate returns a concrete BuilderFrom."""
        template = pydantus.BuilderFrom(Person).partial()

        result = template.new()
        assert isinstance(result, pydantus.BuilderFrom)
        assert result is not template

    def test_partial_partial_returns_self(self):
        """Test that partial() on a BuilderTemplate returns itself."""
        template = pydantus.BuilderFrom(Person).partial()

        assert template.partial() is template

    def test_partial_chaining_works(self):
        """Test that chaining after spawning from partial works correctly."""
        template = pydantus.BuilderFrom(Person).set_parent("Alice").partial()

        # Chain multiple operations after spawning
        result = template.set_name("Bob").set_parent("Changed").build()

        assert result.name == "Bob"
        assert result.parent == "Changed"

    def test_partial_with_nested_builders(self):
        """Test partial works correctly with nested builders."""
        base = pydantus.BuilderFrom(ParentWithNested)
        base.set_name("Parent")
        base.build_from_child().set_value(1)

        template = base.partial()

        # Create two variations with different nested values
        result_a = template.set_name("A").build()
        result_b = template.set_name("B").build()

        # Both should have the original nested value
        assert result_a.child.value == 1
        assert result_b.child.value == 1
        assert result_a.name == "A"
        assert result_b.name == "B"


class TestProtocolCompliance:
    """Tests to verify protocol compliance."""

    def test_builder_from_has_required_methods(self):
        """Test that BuilderFrom has new, partial, and build methods."""
        builder = pydantus.BuilderFrom(Person)

        assert hasattr(builder, "new")
        assert hasattr(builder, "partial")
        assert hasattr(builder, "build")

    def test_template_builder_has_required_methods(self):
        """Test that BuilderTemplate has new, partial, and build methods."""
        template = pydantus.BuilderFrom(Person).partial()

        assert hasattr(template, "new")
        assert hasattr(template, "partial")
        assert hasattr(template, "build")
