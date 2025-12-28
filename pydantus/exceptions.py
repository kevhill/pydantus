"""Pydantus exceptions."""


class BuilderTemplateValueError(TypeError):
    """Raised when a BuilderTemplate is passed where a concrete value is expected.

    BuilderTemplates are immutable and spawn copies on any operation.
    Setting one as a field value would lead to confusing behavior where
    subsequent modifications to the template don't affect the builder's data.

    Use .new() to get a concrete BuilderFrom instance instead:
        builder.set_field(template.new())  # OK
        builder.set_field(template)        # Raises this error
    """

    pass
