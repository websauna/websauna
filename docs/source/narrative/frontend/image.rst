======
Images
======

.. contents:: :local:

Introduction
============

Websauna core doesn't provide any special support for images. Images are served as any other static assets.

Dynamic image resizes
=====================

Below is a recipe for generating dynamic image rescales from URL sources. Images are cached in redis and served with proper HTTP caching headers.

``resizer.py``:

.. code-block:: python

    from io import BufferedIOBase
    from io import BytesIO
    import logging

    from pyramid.httpexceptions import HTTPNotImplemented
    from pyramid.response import Response
    from PIL import Image

    from websauna.system.core.redis import get_redis
    from websauna.system.http import Request


    logger = logging.getLogger(__name__)


    def resized_image(request: Request, cache_key: str, source: BufferedIOBase, width: int, height: int, cache_timeout=30*24*3600, source_content_type=None, format="png") -> Response:
        """Create a resized image version.

        Results are cached in redis.

        :param request: HTTP request related to this
        :param source: Image source as byte stream
        :param width: Desired with
        :param height: Desired height
        :param format: Output format. Either "png" or "jpeg".
        :param cache_timeout: How long cached result is stored in Redis in seconds
        :param source_format: Binary format hint for Pillow to decode image
        :return: Cacheable HTTP response for the image
        """

        # Sanity check and potentially prevent some abuse
        if source_content_type:
            if source_content_type not in ("image/jpeg", "image/png"):
                logger.warn("Unsupported image rescale content type: %s", source_content_type)
                return HTTPNotImplemented()

        # Allow override cache for testing on when giving URL like:
        # http://localhost:6543/cosmos/logo_small?redraw=true
        # This is to fix potential single caes error
        redraw = "redraw" in request.params
        if redraw:
            logger.warn("Forced redraw of image scale")

        redis = get_redis(request)
        full_cache_key = "image_resize_{}_{}_{}_{}".format(cache_key, width, height, format)
        data = redis.get(full_cache_key)
        if not data or redraw:
            size = (width, height)
            img = Image.open(source)
            img = img.convert('RGBA')
            img.thumbnail(size)
            # Alternative cropper implementation
            # img = ImageOps.fit(img, size, Image.ANTIALIAS)
            buf = BytesIO()
            img.save(buf, format=format)
            data = buf.getvalue()
            redis.set(full_cache_key, data, ex=cache_timeout)
            buf.seek(0)
        else:
            buf = BytesIO(data)

        # Streamable response so we don't cause a clog in the series of tubes
        resp = Response(content_type="image/" + format, body_file=buf)

        # Set cache headers for downstream web server
        resp.cache_expires = cache_timeout
        resp.cache_control.public = True
        resp.headers["Content-length"] = str(len(data))

        return resp

Example usage:

.. code-block:: python

    @view_config(context=AssetDescription, route_name="network", name="logo_small.png")
    def logo_small(asset_desc: AssetDescription, request: Request):
        """Create a downscaled logo version for an asset.

        .. note::

            .png suffix in URL is required by some proxies (CloudFlare) to make the response caching to follow the normal caching rules.
        """

        # We have a logo image URL for an item we wish to display
        logo_url = asset_desc.asset.other_data.get("logo")
        if not logo_url:
            return HTTPNotFound()

        # http://stackoverflow.com/a/37547880/315168
        resp = requests.get(logo_url, stream=True)
        resp.raise_for_status()

        resp.raw.decode_content = True
        source_content_type = resp.headers["Content-type"]

        # Cache logos by asset human readable id
        return resized_image(request, "logo_small_" + str(asset_desc.asset.slug), source=resp.raw, source_content_type=source_content_type, width=256, height=256, format="png")

Then in templates:

.. code-block:: html+jinja

    <td class="col-logo">
      <a class=logo-link href="{{ asset_resource|model_url }}">
        <img src="{{ asset_resource|model_url('logo_small') }}">
      </a>

      <a href="{{ asset_resource|model_url }}">
        {{ asset_resource.asset.name }}
      </a>
    </td>