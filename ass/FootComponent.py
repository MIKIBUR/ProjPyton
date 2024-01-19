# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class FootComponent(Component):
    """A FootComponent component.
ExampleComponent is an example component.
It takes a property, `label`, and
displays it.
It renders an input with the property `value`
which is editable by the user.

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- value1 (string; optional):
    The value displayed in the input.

- value2 (string; optional):
    The value displayed in the input.

- value3 (string; optional):
    The value displayed in the input.

- value4 (string; optional):
    The value displayed in the input.

- value5 (string; optional):
    The value displayed in the input.

- value6 (string; optional):
    The value displayed in the input."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'ass'
    _type = 'FootComponent'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, value1=Component.UNDEFINED, value2=Component.UNDEFINED, value3=Component.UNDEFINED, value4=Component.UNDEFINED, value5=Component.UNDEFINED, value6=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'value1', 'value2', 'value3', 'value4', 'value5', 'value6']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'value1', 'value2', 'value3', 'value4', 'value5', 'value6']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(FootComponent, self).__init__(**args)
