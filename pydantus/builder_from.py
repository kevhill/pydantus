from __future__ import annotations

import copy
from typing import Any, Callable, Type, get_args, get_origin

from pydantic import BaseModel

from pydantus.builder_template import BuilderTemplate
from pydantus.protocols import Builder


class BuilderFrom(Builder):
    """Builder for Pydantic models."""

    _PREFIXES = ("set_", "add_", "build_from_")

    def __init__(self, model_class: Type[BaseModel]):
        self._model_class = model_class
        self._data: dict[str, Any] = {}

    def new(self) -> Builder:
        """Create an independent copy of this builder with separate data."""
        new_builder = BuilderFrom(self._model_class)
        new_builder._data = {
            key: value.new() if isinstance(value, Builder) else copy.deepcopy(value)
            for key, value in self._data.items()
        }
        return new_builder

    def partial(self) -> Builder:
        """Create a template builder that spawns copies on any operation."""
        return BuilderTemplate(self)

    def __getattr__(self, name: str):
        """Intercept method calls to handle set_*, add_*, and build_from_* patterns."""
        for prefix in self._PREFIXES:
            if name.startswith(prefix):
                field_name = name[len(prefix) :]
                self._validate_field_name(field_name)
                if prefix == "set_":
                    return self._make_setter(field_name)
                elif prefix == "add_":
                    return self._make_adder(field_name)
                elif prefix == "build_from_":
                    nested_type = self._get_nested_model_type(field_name)
                    return self._get_nested_builder(field_name, nested_type)

        raise AttributeError(
            f"'{type(self).__name__}' has no method '{name}'. "
            f"Methods must start with 'set_', 'add_', or 'build_from_'."
        )

    def _validate_field_name(self, field_name: str) -> None:
        """Validate that a field exists on the model."""
        if field_name not in self._model_class.model_fields:
            raise AttributeError(
                f"'{self._model_class.__name__}' has no field '{field_name}'."
            )

    def _get_nested_model_type(self, field_name: str) -> Type[BaseModel]:
        """Get the BaseModel type for a nested field, validating it's a model."""
        field_type = self._model_class.model_fields[field_name].annotation

        # Handle Optional types and other generic types
        origin = get_origin(field_type)
        if origin is not None:
            args = get_args(field_type)
            # For Optional[X] (Union[X, None]), get the non-None type
            field_type = next((a for a in args if a is not type(None)), field_type)

        # Verify it's a BaseModel subclass
        if not (isinstance(field_type, type) and issubclass(field_type, BaseModel)):
            raise TypeError(
                f"Field '{field_name}' is not a BaseModel subclass, "
                f"cannot create nested builder."
            )

        return field_type

    def _make_setter(self, field_name: str) -> Callable[[Any], "BuilderFrom"]:
        """Create a setter function for the given field."""

        def setter(value: Any) -> "BuilderFrom":
            self._data[field_name] = value
            return self

        return setter

    def _make_adder(self, field_name: str) -> Callable[[Any], "BuilderFrom"]:
        """Create an adder function that appends to a list field."""

        def adder(value: Any) -> "BuilderFrom":
            if field_name not in self._data:
                self._data[field_name] = []
            self._data[field_name].append(value)
            return self

        return adder

    def _get_nested_builder(
        self, field_name: str, nested_type: Type[BaseModel]
    ) -> Callable[[], "BuilderFrom"]:
        """Return a callable that gets or creates a nested builder for a field."""

        def get_builder() -> "BuilderFrom":
            # Return existing builder if already in _data
            existing = self._data.get(field_name)
            if isinstance(existing, Builder):
                return existing

            nested_builder = BuilderFrom(nested_type)
            self._data[field_name] = nested_builder
            return nested_builder

        return get_builder

    def _resolve_value(self, value: Any) -> Any:
        """Recursively resolve Builder instances to their built models."""
        if isinstance(value, Builder):
            return value.build()
        if isinstance(value, list):
            return [self._resolve_value(item) for item in value]
        return value

    def build(self) -> BaseModel:
        """Build and return the model instance."""
        build_data = {
            field_name: self._resolve_value(value)
            for field_name, value in self._data.items()
        }
        return self._model_class(**build_data)
