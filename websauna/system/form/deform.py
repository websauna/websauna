"""Deform specific initialization logic."""
# Pyramid
import deform

from pkg_resources import resource_filename


def configure_zpt_renderer(search_path=()):
    """Initialize ZPT widget rendering for Deform forms.

    See https://github.com/Pylons/pyramid_deform/blob/master/pyramid_deform/__init__.py#L437
    """

    default_paths = deform.form.Form.default_renderer.loader.search_path
    paths = []
    for path in search_path:
        pkg, resource_name = path.split(':')
        paths.append(resource_filename(pkg, resource_name))
    deform.form.Form.default_renderer = deform.ZPTRendererFactory(
        tuple(paths) + default_paths)
