"""Registering static assets with cache busting policies."""
import json
import logging
from collections import defaultdict

import shutil
import hashlib

import os
from pyramid.decorator import reify

try:
    from os import scandir
except ImportError:
    from scandir import scandir

from abc import ABC, abstractmethod
from pyramid.config import Configurator
from pyramid.path import AssetResolver
from waitress.adjustments import asbool


logger = logging.getLogger(__name__)


MARKER_FOLDER = "perma-asset"


# Courtesy of http://stackoverflow.com/a/3431838/315168
def md5(fname):
    hash = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()


class CopyAndHashCollector:
    """Toss all static files to a certain path on filesystem, MD5 hash included in the name."""

    def __init__(self, settings: dict, target_path=None):
        self.settings= settings
        target_path = target_path or self.settings.get("websauna.collected_static_path")
        assert target_path, "No websauna.collected_static_path configured"

        self.target_path = target_path
        self.collected = defaultdict(dict)

    def get_permanent_path(self, root, static_view_name, relative_path, hash):

        base_file, ext = os.path.splitext(relative_path)
        ext = "." + hash + ext
        relative_path = base_file + ext

        return os.path.join(root, MARKER_FOLDER, relative_path)

    def process(self, root, static_view_name, entry, relative_path):
        """Make a persistent copy of a file.

        :param entry: Scandir entry of a file
        """
        hash = md5(entry.path)
        target = self.get_permanent_path(root, static_view_name, relative_path, hash)
        rel_target = os.path.relpath(target, root)

        if os.path.exists(target):
            # Let's avoid unnecessary copy
            if os.path.getsize(target) == entry.stat().st_size:
                # Same size, not a corrupted copy
                return rel_target

        dir = os.path.dirname(target)
        os.makedirs(dir, exist_ok=True)

        # Create a permanent copy
        shutil.copy(entry.path, target)

        return rel_target

    def collect(self, root, static_view_name, entry, relative_path):
        """Process one file and add it to our collection."""
        target = self.process(root, static_view_name, entry, relative_path)
        by_view = self.collected[static_view_name]
        by_view[relative_path] = target

        logger.info("Collected %s:%s as %s", static_view_name, relative_path, target)

    def finish(self):
        manifest_path = os.path.join(self.target_path, "manifest.json.tmp")
        with open(manifest_path, "wt") as f:
            json.dump(self.collected, f)

        # Atomic replacement
        # Dotted files should not be accessible through normal static file serving
        os.rename(manifest_path, os.path.join(self.target_path, ".manifest.json"))
        return self.collected


class StaticAssetPolicy(ABC):
    """A helper class to add static paths and apply a cache busting policy on them.

    """

    def __init__(self, config: Configurator):
        self.config = config

    @abstractmethod
    def add_static_view(self, name: str, path: str):
        """Include a path in static assets and configures cache busting for it.

        This does not only include the static resources in the routing, but sets the default cache busting policy for them in the :term:`production` environment.

        See :py:meth:`pyramid.config.Configurator.add_static_view` and :py:meth:`websauna.system.Initializer.add_cache_buster`
        """


class DefaultStaticAssetPolicy(StaticAssetPolicy):

    def __init__(self, config: Configurator):
        self.config = config
        self.settings = config.registry.settings

        #: Maintain registry of all registered static views
        self.views = {}

        # Collector which sweeps static resources to their persistent storage
        self.collector = CopyAndHashCollector(self.settings)

        self.prepare_collected_static_view()

    def prepare_collected_static_view(self):
        """Setup the view which serves collected cached resources."""
        collected_static_path = self.settings.get("websauna.collected_static_path")
        self.add_static_view("collected-static", collected_static_path)

    def get_cache_max_age(self):
        """Get websauna.cache_max_age setting and convert it to seconds.

        :return: None for no caching or cache_max_age as seconds
        """
        cache_max_age = self.settings.get("websauna.cache_max_age_seconds")
        if (not cache_max_age) or (not cache_max_age.strip()):
            return None
        else:
            return int(cache_max_age)

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
            self.config.add_cache_buster(path, CollectedStaticCacheBuster(name, self.settings))

        self.views[name] = path

    def collect_static(self):
        """Collect all static files from all static views for the manifest."""

        r = AssetResolver()
        for name, asset_spec in self.views.items():

            root = r.resolve(asset_spec).abspath()

            for entry in scandir(root):

                if entry.name.startswith("."):
                    # Dot files are usually backups or other no no files
                    continue

                # Don't process our internal cache folder
                if MARKER_FOLDER in entry.path:
                    continue

                relative = os.path.relpath(entry.path, root)

                if entry.is_file():
                    self.collector.collect(root, name, entry, relative)


        return self.collector.finish()



class CollectedStaticCacheBuster:
    """A Pyramid cache buster which uses persistent static item folder from ws-collect-static command to serve static assets."""

    def __init__(self, static_view_name, settings: dict):
        self.settings = settings
        self.static_view_name = static_view_name
        self.target_path = self.settings.get("websauna.collected_static_path")
        assert self.target_path, "No websauna.collected_static_path configured"

    @reify
    def manifest(self):
        target_f = os.path.join(self.target_path, ".manifest.json")
        assert os.path.exists(target_f), "websauna.collected_static manifest does not exist: {}. Did you run ws-collect-static command?".format(target_f)
        with open(target_f, "rt") as f:
            full_manifest = json.load(f)

        # Each view has its own fileset inside cache manifest
        assert self.static_view_name in full_manifest, "Cache manifest did not contain cache data for view {}, contained {}".format(self.static_view_name, full_manifest.keys())

        return full_manifest[self.static_view_name]

    def __call__(self, request, subpath, kw):
        subpath = self.manifest.get(subpath, subpath)
        return ("collect-static/" + subpath, kw)


