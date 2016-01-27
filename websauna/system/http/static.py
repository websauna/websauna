"""Registering static assets with cache busting policies.

For more information read :ref:`static` narrative.
"""
from abc import ABC, abstractmethod
import json
import logging
from collections import defaultdict
import shutil
import hashlib

import os

try:
    from os import scandir
except ImportError:
    from scandir import scandir

from pyramid.decorator import reify
from pyramid.config import Configurator
from pyramid.path import AssetResolver


logger = logging.getLogger(__name__)


MARKER_FOLDER = "perma-asset"

#: Generated at the root of each perma-asset folder
MANIFEST_FILE = ".manifest.json"


class StaticAssetPolicy(ABC):
    """A helper class to add static views and apply a configured cache busting policy on them."""

    def __init__(self, config: Configurator):
        self.config = config

    @abstractmethod
    def add_static_view(self, name: str, path: str):
        """Include a path in static assets and configures cache busting for it.

        This does not only include the static resources in the routing, but sets the default cache busting policy for them in the :term:`production` environment.

        See :py:meth:`pyramid.config.Configurator.add_static_view` for more details.
        """


# Courtesy of http://stackoverflow.com/a/3431838/315168
def md5(fname):
    hash = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()


class CopyAndHashCollector:
    """Toss all static files into perma-asset folder, MD5 hash included in the name."""

    def __init__(self, root: str, settings: dict, target_path=None):
        self.root = root
        self.settings= settings
        self.collected = defaultdict(dict)

    def get_permanent_path(self, root, static_view_name, relative_path, hash):

        base_file, ext = os.path.splitext(relative_path)
        ext = "." + hash + ext
        relative_path = base_file + ext

        return os.path.join(self.root, MARKER_FOLDER, relative_path)

    def process(self, root, static_view_name, entry, relative_path):
        """Make a persistent copy of a file.

        :param entry: Scandir entry of a file
        """
        hash = md5(entry.path)
        target = self.get_permanent_path(root, static_view_name, relative_path, hash)
        rel_target = os.path.relpath(target, self.root)

        if os.path.exists(target):
            # Let's avoid unnecessary copy
            if os.path.getsize(target) == entry.stat().st_size:
                # Same size, not a corrupted copy
                return rel_target

        dir = os.path.dirname(target)
        os.makedirs(dir, exist_ok=True)

        # Create a permanent copy
        shutil.copy(entry.path, target)
        logger.info("Writing %s", target)

        return rel_target

    def collect(self, root, static_view_name, entry, relative_path):
        """Process one file and add it to our collection."""
        target = self.process(root, static_view_name, entry, relative_path)
        by_view = self.collected[static_view_name]
        by_view[relative_path] = target
        self.process(root, static_view_name, entry, relative_path)
        logger.info("Collected %s:%s as %s", static_view_name, relative_path, target)

    def finish(self):

        manifest_path = os.path.join(self.root, MARKER_FOLDER, "manifest.json.tmp")

        dirs = os.path.dirname(manifest_path)
        os.makedirs(dirs, exist_ok=True)

        with open(manifest_path, "wt") as f:
            json.dump(self.collected, f)

        # Atomic replacement
        # Dotted files should not be accessible through normal static file serving
        os.rename(manifest_path, os.path.join(self.root, MARKER_FOLDER, MANIFEST_FILE))
        return self.collected


class DefaultStaticAssetPolicy(StaticAssetPolicy):

    def __init__(self, config: Configurator):
        super(DefaultStaticAssetPolicy, self).__init__(config)
        self.settings = config.registry.settings

        #: Maintain registry of all registered static views
        self.views = {}

    def add_static_view(self, name: str, path: str):
        """Include a path in static assets and configures cache busting for it.

        This does not only include the static resources in the routing, but sets the default cache busting policy for them in the :term:`production` environment.

        See :py:meth:`pyramid.config.Configurator.add_static_view` and :py:meth:`websauna.system.Initializer.add_cache_buster`
        """

        # Default value is 0
        cache_max_age = self.settings.get("websauna.cache_max_age_seconds")
        if cache_max_age:
            cache_max_age = int(cache_max_age)

        self.config.add_static_view(name, path, cache_max_age=cache_max_age)

        # If we have caching... we need cachebusters!
        if cache_max_age:
            self.config.add_cache_buster(path, CollectedStaticCacheBuster(name, path, self.settings))

        self.views[name] = path

    def collect_static(self):
        """Collect all static files from all static views for the manifest."""

        def recurse(collector, path):

            for entry in scandir(path):

                if entry.name.startswith("."):
                    # Dot files are usually backups or other no no files
                    continue

                # Don't process our internal cache folder
                if MARKER_FOLDER in entry.path:
                    continue

                relative = os.path.relpath(entry.path, collector.root)

                if entry.is_file():
                    collector.collect(path, name, entry, relative)
                elif entry.is_dir():
                    recurse(collector, entry.path)

        r = AssetResolver()
        for name, asset_spec in self.views.items():

            root = r.resolve(asset_spec).abspath()
            collector = CopyAndHashCollector(root, self.settings)
            recurse(collector, root)
            results = collector.finish()

        # Expose for testing
        return results


class CollectedStaticCacheBuster:
    """A Pyramid cache buster which uses persistent static item folder from ws-collect-static command to serve static assets."""

    def __init__(self, static_view_name, path, settings: dict):
        self.settings = settings
        self.static_view_name = static_view_name
        r = AssetResolver()
        self.root = r.resolve(path).abspath()

    @reify
    def manifest(self):
        """Read manifest file which maps filenames to their MD5 stamped counterparts."""
        target_f = os.path.join(self.root, MARKER_FOLDER, MANIFEST_FILE)
        assert os.path.exists(target_f), "websauna.collected_static manifest does not exist: {}. Did you run ws-collect-static command?".format(target_f)
        with open(target_f, "rt") as f:
            full_manifest = json.load(f)

        # Each view has its own fileset inside cache manifest
        assert self.static_view_name in full_manifest, "Cache manifest did not contain cache data for view {}, contained {}".format(self.static_view_name, full_manifest.keys())

        return full_manifest[self.static_view_name]

    def __call__(self, request, subpath, kw):
        """Map a path to perma-asset path."""
        subpath = self.manifest.get(subpath, subpath)
        return (subpath, kw)


