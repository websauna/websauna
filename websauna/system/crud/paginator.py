"""Paginator."""
# Standard Library
import math
import typing as t
from urllib.parse import parse_qsl
from urllib.parse import urlencode
from urllib.parse import urlsplit
from urllib.parse import urlunsplit


def merge_url_qs(url: str, **kw) -> str:
    """Merge the query string elements of a URL with the ones in ``kw``.

    If any query string element exists in ``url`` that also exists in ``kw``, replace it.

    :param url: An URL.
    :param kw: Dictionary with keyword arguments.
    :return: An URL with keyword arguments merged into the query string.
    """
    segments = urlsplit(url)
    extra_qs = [
        (k, v)
        for (k, v) in parse_qsl(segments.query, keep_blank_values=1)
        if k not in kw
    ]
    qs = urlencode(sorted(kw.items()))
    if extra_qs:
        qs += '&' + urlencode(extra_qs)
    return urlunsplit((segments.scheme, segments.netloc, segments.path, qs, segments.fragment))


class Batch:
    """Present one paginator batch in the list rendering output.

    Originally courtesy of SubstanceD project.

    Given a sequence named ``seq``, and a Pyramid request, return an
    object with the following attributes:

    ``items``

      A list representing a slice of ``seq``.  It will contain the number of
      elements in ``request.params['batch_size']`` or the ``default_size``
      number if such a key does not exist in request.params or the key is
      invalid.  The slice will begin at ``request.params['batch_num']`` or
      zero if such a key does not exist in ``request.params`` or the
      ``batch_num`` key could not successfully be converted to a positive
      integer.

      This value can be iterated over via the ``__iter__`` of the batch
      object.

    ``size``

      The value obtained from ``request.params['batch_size']`` or
      ``default_size`` if no ``batch_size`` parameter exists in
      ``request.params`` or the ``batch_size`` parameter could not
      successfully be converted to a positive interger.

    ``num``

      The value obtained from ``request.params['batch_num']`` or ``0`` if no
      ``batch_num`` parameter exists in ``request.params`` or if the
      ``batch_num`` parameter could not successfully be converted to a
      positive integer.  Batch numbers are indexed from zero, so batch ``0``
      is the first batch, batch ``1`` the second, and so forth.

    ``length``

      This is length of the current batch.  It is usually equal to ``size``
      but may be different in the very last batch.  For example, if the
      ``seq`` is ``[1,2,3,4]`` and the batch size is ``3``, the first batch's
      ``length`` will be ``3`` because the batch content will be ``[1,2,3]``;
      but the second and final batch's ``length`` will be ``1`` because the
      batch content will be ``[4]``.

    ``last``

      The batch number computed from the sequence length of the last batch
      (indexed from zero).

    ``first_url``

      The URL of the first batch.  This will be a URL with ``batch_num`` and
      ``batch_size`` in its query string.  The base URL will be taken from
      the ``url`` value passed to this function.  If a ``url`` value is not
      passed to this function, the URL will be taken from ``request.url``.
      This value will be ``None`` if the current ``batch_num`` is 0.

    ``prev_url``

      The URL of the previous batch.  This will be a URL with ``batch_num``
      and ``batch_size`` in its query string.  The base URL will be taken
      from the ``url`` value passed to this function.  If a ``url`` value is
      not passed to this function, the URL will be taken from
      ``request.url``.  This value will be ``None`` if there is no previous
      batch.

    ``next_url``

      The URL of the next batch.  This will be a URL with ``batch_num`` and
      ``batch_size`` in its query string.  The base URL will be taken from
      the ``url`` value passed to this function.  If a ``url`` value is not
      passed to this function, the URL will be taken from ``request.url``.
      This value will be ``None`` if there is no next batch.

    ``last_url``

      The URL of the next batch.  This will be a URL with ``batch_num`` and
      ``batch_size`` in its query string.  The base URL will be taken from
      the ``url`` value passed to this function.  If a ``url`` value is not
      passed to this function, the URL will be taken from ``request.url``.
      This value will be ``None`` if there is no next batch.

    ``required``

      ``True`` if either ``next_url`` or ``prev_url`` are ``True`` (meaning
      batching is required).

    ``multicolumn``

      ``True`` if the current view should be rendered in multiple columns.

    ``toggle_url``

      The URL to be used for the multicolumn/single column toggle button. The
      ``batch_size``, ``batch_num``, and ``multicolumn`` parameters are
      converted to their multicolumn or single column equivalents. If a user
      is viewing items 40-80 in multiple columns, the toggle will switch to
      items 40-50 in a single column. If a user is viewing items 50-60 in a
      single column, the toggle will switch to items 40-80 in multiple columns.

    ``toggle_text``

      The text to display on the multi-column/single column toggle.

    ``make_columns``

      A method to split ``items`` into a nested list representing columns.

    ``seqlen``

      This is total length of the sequence (across all batches).

    ``startitem``

      The item number that starts this batch (indexed from zero).

    ``enditem``

      The item number that ends this batch (indexed from zero).

    """
    def __init__(self, seq, request, url=None, default_size=10, toggle_size=40,
                 seqlen=None):
        if url is None:
            url = request.url

        try:
            num = int(request.params.get('batch_num', 0))
        except (TypeError, ValueError):
            num = 0
        if num < 0:
            num = 0

        try:
            size = int(request.params.get('batch_size', default_size))
        except (TypeError, ValueError):
            size = default_size
        if size < 1:
            size = default_size

        multicolumn = request.params.get('multicolumn', '') == 'True'

        # create multicolumn/single column toggle attributes
        if multicolumn:
            toggle_num = size * num / default_size
            toggle_size = default_size
            toggle_text = 'Single column'
        else:
            toggle_num = size * num / toggle_size
            toggle_text = 'Multi-column'

        if seqlen is None:
            # won't work if seq is a generator
            seqlen = len(seq)
        start = num * size
        end = start + size
        if end > seqlen:
            end = seqlen

        # normal list slicing is mucho faster than islice
        items = seq[start:end]

        length = len(items)
        last = int(math.ceil(seqlen / float(size)) - 1)

        first_url = None
        prev_url = None
        next_url = None
        last_url = None
        toggle_url = None

        if num:
            first_url = merge_url_qs(url, batch_size=size, batch_num=0)
        if start >= size:
            prev_url = merge_url_qs(url, batch_size=size, batch_num=num - 1)
        if seqlen > end:
            next_url = merge_url_qs(url, batch_size=size, batch_num=num + 1)
        if size and (num < last):
            last_url = merge_url_qs(url, batch_size=size, batch_num=last)

        if prev_url or next_url:
            toggle_url = merge_url_qs(
                url,
                batch_size=toggle_size,
                batch_num=toggle_num,
                multicolumn=not multicolumn,
            )

        self.startitem = start
        self.enditem = end - 1
        self.last = last
        self.seqlen = seqlen
        self.items = items
        self.num = num
        self.size = size
        self.length = length
        self.required = bool(prev_url or next_url)
        self.multicolumn = multicolumn
        self.toggle_url = toggle_url
        self.toggle_text = toggle_text
        self.first_url = first_url
        self.prev_url = prev_url
        self.next_url = next_url
        self.last_url = last_url

    def make_columns(self, column_size=10, num_columns=4):
        """ Break ``self.items`` into a nested list representing columns."""
        columns = []
        for i in range(num_columns):
            start = i * column_size
            end = start + column_size
            part = self.items[start:end]
            columns.append(part)
        return columns

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return self.length

    def __nonzero__(self):
        return True

    __bool__ = __nonzero__  # py3


class DefaultPaginator:
    """Default pagination implementation for CRUD, having 20 items per page."""

    template = 'crud/paginator.html'

    default_size = 20

    def __init__(self, template: t.Optional[str]=None, default_size: t.Optional[int]=None):
        """Initialize DefaultPaginator.

        :param template: Path to paginator template.
        :param default_size: Pagination size.
        """
        if template:
            self.template = template

        if default_size:
            self.default_size = default_size

    def paginate(self, seq, request, count, url=None) -> Batch:
        batch = Batch(seq, request, seqlen=count, url=url, default_size=self.default_size)
        return batch
