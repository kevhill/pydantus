"""Protocol definitions for Pydantus builders."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from pydantic import BaseModel


@runtime_checkable
class Builder(Protocol):
    """Protocol defining the builder interface.

    Builders support dynamic method access for:
    - set_<field>(value) -> Builder: Set a field value
    - add_<field>(value) -> Builder: Append to a list field
    - build_from_<field>() -> Builder: Get/create nested builder

    These dynamic methods are handled via __getattr__ and return
    the builder instance for chaining.
    """

    def new(self) -> Builder:
        """Create an independent copy of this builder with separate data."""
        ...

    def partial(self) -> Builder:
        """Create a template builder that spawns copies on any operation."""
        ...

    def build(self) -> BaseModel:
        """Build and return the model instance."""
        ...
