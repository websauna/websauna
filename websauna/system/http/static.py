"""Registering static assets with cache busting policies.

For more information read :ref:`static` narrative.
"""
# Standard Library
import hashlib
import json
import logging
import os
import shutil
import typing as t
from abc import ABC
from abc import abstractmethod
from collections import defaultdict
from os import scandir

# Pyramid
from pyramid.config import Configurator
from pyramid.decorator import reify
from pyramid.path import AssetResolver
from pyramid.request import Request

# Websauna
from websauna.compat.typing import DirEntry


logger = logging.getLogger(__name__)


MARKER_FOLDER = "perma-asset"

#: Generated at the root of each perma-asset folder
MANIFEST_FILE = ".manifest.json"


class StaticAssetPolicy(ABC):
    """A helper class to add static views and apply a configured cache busting policy on them."""

    def __init__(self, config: Configurator):
        """Initialize the StaticAssetPolicy.

        :param config: Pyramid configuration.
        """
        self.config = config

    @abstractmethod
    def add_static_view(self, name: str, path: str):
        """Include a path in static assets and configures cache busting for it.

        This does not only include the static resources in the routing, but sets the default cache busting policy for them in the :term:`production` environment.

        See :py:meth:`pyramid.config.Configurator.add_static_view` for more details.

        :param name: Name of the asset.
        :param path: Path to the asset.
        """


# Courtesy of http://stackoverflow.com/a/3431838/315168
def md5(filename: str) -> str:
    """Generate the md5 hash for a file with given filename.

    :param filename: Name of the file to generate the MD5 hash for.
    :return: md5 hash of the file.
    """
    hash = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()


class CopyAndHashCollector:
    """Toss all static files into perma-asset folder, MD5 hash included in the name."""

    def __init__(self, root: str, settings: dict, target_path: str=None):
        """Initialize CopyAndHashCollector.

        :param root: Root path.
        :param settings: Configuration.
        :param target_path: Destination path.
        """
        self.root = root
        self.settings = settings
        self.collected = defaultdict(dict)

    def get_permanent_path(self, root: str, static_view_name: str, relative_path: str, hash: str) -> str:
        """Return the permanent path for an asset.

        :param root: Root path.
        :param static_view_name: Name of the asset.
        :param relative_path: Relative path of the asset.
        :param hash: Hash of the file.
        :return: Permanent path to the asset.
        """
        base_file, ext = os.path.splitext(relative_path)
        ext = '.{hash}{ext}'.format(hash=hash, ext=ext)
        relative_path = base_file + ext
        return os.path.join(self.root, MARKER_FOLDER, relative_path)

    def process(self, root: str, static_view_name: str, entry: DirEntry, relative_path: str) -> str:
        """Make a persistent copy of a file.

        :param root: Root path.
        :param static_view_name: Asset name.
        :param entry: DirEntry for asset.
        :param relative_path: Relative path of the asset.
        :return: Permanent path to the asset
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
        logger.info('Writing %s', target)
        return rel_target

    def collect(self, root: str, static_view_name: str, entry: DirEntry, relative_path: str):
        """Process one file and add it to our collection.

        :param root: Root path.
        :param static_view_name: Asset name.
        :param entry: DirEntry for asset.
        :param relative_path: Relative path of the asset.
        """
        target = self.process(root, static_view_name, entry, relative_path)
        by_view = self.collected[static_view_name]
        by_view[relative_path] = target
        self.process(root, static_view_name, entry, relative_path)
        logger.info('Collected %s:%s as %s', static_view_name, relative_path, target)

    def finish(self) -> dict:
        """Finish collection and create manifest.json file.

        :return: Collected files.
        """
        manifest_path = os.path.join(self.root, MARKER_FOLDER, 'manifest.json.tmp')
        dirs = os.path.dirname(manifest_path)
        os.makedirs(dirs, exist_ok=True)
        with open(manifest_path, 'wt') as f:
            json.dump(self.collected, f)
        # Atomic replacement
        # Dotted files should not be accessible through normal static file serving
        os.rename(manifest_path, os.path.join(self.root, MARKER_FOLDER, MANIFEST_FILE))
        return self.collected


class DefaultStaticAssetPolicy(StaticAssetPolicy):
    """Default inplementation of StaticAssetPolicy."""

    def __init__(self, config: Configurator):
        """Initialize DefaultStaticAssetPolicy.

        :param config: Pyramid config.
        """
        super(DefaultStaticAssetPolicy, self).__init__(config)
        self.settings = config.registry.settings

        #: Maintain registry of all registered static views
        self.views = {}

    def add_static_view(self, name: str, path: str):
        """Include a path in static assets and configures cache busting for it.

        This does not only include the static resources in the routing, but sets the default cache busting policy for them in the :term:`production` environment.

        See :py:meth:`pyramid.config.Configurator.add_static_view` and :py:meth:`websauna.system.Initializer.add_cache_buster`

        :param name: Asset name.
        :param path: Asset path.
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

    def collect_static(self) -> dict:
        """Collect all static files from all static views for the manifest.

        :return: Collect assets.
        """
        results = defaultdict(dict)

        def recurse(collector: CopyAndHashCollector, path: str):
            """Recursively collect assets.

            :param collector: CopyAndHashCollector instance
            :param path: Path to collect assets.
            """
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

    def __init__(self, static_view_name: str, path: str, settings: dict):
        """Initialize CollectedStaticCacheBuster.

        :param static_view_name: Asset name.
        :param path: Asset path.
        :param settings: Configurations.
        """
        self.settings = settings
        self.static_view_name = static_view_name
        r = AssetResolver()
        self.root = r.resolve(path).abspath()

    @reify
    def manifest(self) -> dict:
        """Read manifest file which maps filenames to their MD5 stamped counterparts.

        :return: Manifest entry for a view.
        """
        target_f = os.path.join(self.root, MARKER_FOLDER, MANIFEST_FILE)
        assert os.path.exists(target_f), "websauna.collected_static manifest does not exist: {path}. Did you run ws-collect-static command?".format(path=target_f)
        with open(target_f, "rt") as f:
            full_manifest = json.load(f)

        # Each view has its own fileset inside cache manifest
        assert self.static_view_name in full_manifest, "Cache manifest did not contain cache data for view {view}, contained {keys}".format(
            view=self.static_view_name,
            keys=full_manifest.keys()
        )
        return full_manifest[self.static_view_name]

    def __call__(self, request: Request, subpath: str, kw: dict) -> t.Tuple[str, dict]:
        """Map a path to perma-asset path.

        :param request: Pyramid request.
        :param subpath: Asset path.
        :param kw: Settings.
        :return: Tuple with perma-asset path and kw.
        """
        perma_subpath = self.manifest.get(subpath, subpath)
        return perma_subpath, kw
