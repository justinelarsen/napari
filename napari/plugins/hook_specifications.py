"""
All napari hook specifications for pluggable functionality are defined here.

A *hook specification* is a function signature (with documentation) that
declares an API that plugin developers must adhere to when providing hook
implementations.  *Hook implementations* provided by plugins (and internally by
napari) will then be invoked in various places throughout the code base.

When implementing a hook specification, pay particular attention to the number
and types of the arguments in the specification signature, as well as the
expected return type.

To allow for hook specifications to evolve over the lifetime of napari,
hook implementations may accept *fewer* arguments than defined in the
specification. (This allows for extending existing hook arguments without
breaking existing implementations). However, implementations must not require
*more* arguments than defined in the spec.

Hook specifications are a feature of
`pluggy <https://pluggy.readthedocs.io/en/latest/#specs>`_.

.. NOTE::
    in the `pluggy documentation <https://pluggy.readthedocs.io/en/latest/>`_,
    hook specification marker instances are named ``hookspec`` by convention,
    and hook implementation marker instances are named ``hookimpl``.  The
    convention in napari is to name them more explicity:
    ``napari_hook_specification`` and ``napari_hook_implementation``,
    respectively.
"""

# These hook specifications also serve as the API reference for plugin
# developers, so comprehensive documentation with complete type annotations is
# imperative!

import pluggy
from typing import Optional, Union, List
from ..types import ReaderFunction

napari_hook_specification = pluggy.HookspecMarker("napari")


# -------------------------------------------------------------------------- #
#                                 IO Hooks                                   #
# -------------------------------------------------------------------------- #


@napari_hook_specification(firstresult=True)
def napari_get_reader(path: Union[str, List[str]]) -> Optional[ReaderFunction]:
    """Return a function capable of loading ``path`` into napari, or ``None``.

    This is the primary "**reader plugin**" function.  It accepts a path or
    list of paths, and returns a list of data to be added to the ``Viewer``.

    The main place this hook is used is in :func:`Viewer.open_path()
    <napari.components.add_layers_mixin.AddLayersMixin.open_path>`, via the
    :func:`~napari.plugins.io.read_data_with_plugins` function.

    It will also be called on ``File -> Open...`` or when a user drops a file
    or folder onto the viewer. This function must execute *quickly*, and should
    return ``None`` if the filepath is of an unrecognized format for this
    reader plugin.  If ``path`` is determined to be recognized format, this
    function should return a *new* function that accepts the same filepath (or
    list of paths), and returns a list of ``LayerData`` tuples, where each
    tuple is a 1-, 2-, or 3-tuple of ``(data,)``, ``(data, meta)``, or ``(data,
    meta, layer_type)`` .

    ``napari`` will then use each tuple in the returned list to generate a new
    layer in the viewer using the :func:`Viewer._add_layer_from_data()
    <napari.components.add_layers_mixin.AddLayersMixin._add_layer_from_data>`
    method.  The first, (optional) second, and (optional) third items in each
    tuple in the returned layer_data list, therefore correspond to the
    ``data``, ``meta``, and ``layer_type`` arguments of the
    :func:`Viewer._add_layer_from_data()
    <napari.components.add_layers_mixin.AddLayersMixin._add_layer_from_data>`
    method, respectively.


    .. important::

       ``path`` may be either a ``str`` or a ``list`` of ``str``.  If a
       ``list``, then each path in the list can be assumed to be one part of a
       larger multi-dimensional stack (for instance: a list of 2D image files
       that should be stacked along a third axis). Implementations should do
       their own checking for ``list`` or ``str``, and handle each case as
       desired.

    Parameters
    ----------
    path : str or list of str
        Path to file, directory, or resource (like a URL), or a list of paths.

    Returns
    -------
    Callable or None
        A function that accepts the path, and returns a list of ``layer_data``,
        where ``layer_data`` is one of ``(data,)``, ``(data, meta)``, or
        ``(data, meta, layer_type)``.
        If unable to read the path, must return ``None`` (not ``False``!).
    """
