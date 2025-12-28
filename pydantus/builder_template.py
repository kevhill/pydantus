"""Builder template implementation for immutable builder patterns."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from pydantus.protocols import Builder


class BuilderTemplate(Builder):
    """A template that spawns builder copies on any operation.

    Holds a reference to a source builder and spawns a fresh copy
    whenever any mutating operation is performed. This enables
    creating multiple variations from a common base:

        children = builder.set_parent('personA').template()
        child_a = children.set_name('alice').build()
        child_b = children.set_name('bob').build()

    Dynamic methods (set_*, add_*, build_from_*) spawn a copy and
    delegate to it, returning the copy (not the BuilderTemplate).
    """

    def __init__(self, source: Builder) -> None:
        self._source = source

    def new(self) -> Builder:
        """Spawn a fresh copy of the underlying builder."""
        return self._source.new()

    def template(self) -> BuilderTemplate:
        """Return self - the template is already a template."""
        return self

    def build(self) -> BaseModel:
        """Spawn a copy and build the model."""
        return self._source.new().build()

    def __getattr__(self, name: str) -> Any:
        """Spawn a copy and delegate any builder method to it."""
        copy = self._source.new()
        return getattr(copy, name)
