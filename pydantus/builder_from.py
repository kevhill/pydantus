from typing import Any, Type
from pydantic import BaseModel


class BuilderFrom:
    """Builder for Pydantic models."""

    _PREFIXES = ("set_", "add_")

    def __init__(self, model_class: Type[BaseModel]):
        self._model_class = model_class
        self._data: dict[str, Any] = {}

    def __getattr__(self, name: str):
        """Intercept method calls to handle set_* and add_* patterns."""
        for prefix in self._PREFIXES:
            if name.startswith(prefix):
                field_name = name[len(prefix) :]
                if prefix == "set_":
                    return self._make_setter(field_name)
                else:  # add_
                    return self._make_adder(field_name)

        raise AttributeError(
            f"'{type(self).__name__}' has no method '{name}'. "
            f"Methods must start with 'set_' or 'add_'."
        )

    def _make_setter(self, field_name: str):
        """Create a setter function for the given field."""

        def setter(value: Any) -> "BuilderFrom":
            self._data[field_name] = value
            return self

        return setter

    def _make_adder(self, field_name: str):
        """Create an adder function that appends to a list field."""

        def adder(value: Any) -> "BuilderFrom":
            if field_name not in self._data:
                self._data[field_name] = []
            self._data[field_name].append(value)
            return self

        return adder

    def build(self) -> BaseModel:
        """Build and return the model instance."""
        return self._model_class(**self._data)
