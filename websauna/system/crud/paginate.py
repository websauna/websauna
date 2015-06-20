# Copyright (c) 2007-2012 Christoph Haas <email@christoph-haas.de>
# See the file LICENSE for copying permission.

"""
paginate: helps split up large collections into individual pages
================================================================

What is pagination?
---------------------

This module helps split large lists of items into pages. The user is shown one page at a time and
can navigate to other pages. Imagine you are offering a company phonebook and let the user search
the entries. The entire search result may contains 23 entries but you want to display no more than
10 entries at once. The first page contains entries 1-10, the second 11-20 and the third 21-23.
Each "Page" instance represents the items of one of these three pages.

See the documentation of the "Page" class for more information.

How do I use it?
------------------

A page of items is represented by the *Page* object. A *Page* gets initialized with these arguments:

- The collection of items to pick a range from. Usually just a list.
- The page number you want to display. Default is 1: the first page.

Now we can make up a collection and create a Page instance of it::

    # Create a sample collection of 1000 items
    >> my_collection = range(1000)

    # Create a Page object for the 3rd page (20 items per page is the default)
    >> my_page = Page(my_collection, page=3)

    # The page object can be printed as a string to get its details
    >> str(my_page)
    Page:
    Collection type:  <type 'range'>
    Current page:     3
    First item:       41
    Last item:        60
    First page:       1
    Last page:        50
    Previous page:    2
    Next page:        4
    Items per page:   20
    Number of items:  1000
    Number of pages:  50

    # Print a list of items on the current page
    >> my_page.items
    [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59]

    # The *Page* object can be used as an iterator:
    >> for my_item in my_page: print(my_item)
    40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59

    # The .pager() method returns an HTML fragment with links to surrounding pages.
    >> my_page.pager(url="http://example.org/foo/page=$page")

    <a href="http://example.org/foo/page=1">1</a>
    <a href="http://example.org/foo/page=2">2</a>
    3
    <a href="http://example.org/foo/page=4">4</a>
    <a href="http://example.org/foo/page=5">5</a>
    ..
    <a href="http://example.org/foo/page=50">50</a>'

    # Without the HTML it would just look like:
    # 1 2 [3] 4 5 .. 50

    # The pager can be customized:
    >> my_page.pager('$link_previous ~3~ $link_next (Page $page of $page_count)',
                     url="http://example.org/foo/page=$page")

    <a href="http://example.org/foo/page=2">&lt;</a>
    <a href="http://example.org/foo/page=1">1</a>
    <a href="http://example.org/foo/page=2">2</a>
    3
    <a href="http://example.org/foo/page=4">4</a>
    <a href="http://example.org/foo/page=5">5</a>
    <a href="http://example.org/foo/page=6">6</a>
    ..
    <a href="http://example.org/foo/page=50">50</a>
    <a href="http://example.org/foo/page=4">&gt;</a>
    (Page 3 of 50)

    # Without the HTML it would just look like:
    # 1 2 [3] 4 5 6 .. 50 > (Page 3 of 50)

    # The url argument to the pager method can be omitted when an url_maker is
    # given during instantiation:
    >> my_page = Page(my_collection, page=3,
                      url_maker=lambda p: "http://example.org/%s" % p)
    >> page.pager()

There are some interesting parameters that customize the Page's behavior. See the documentation on
``Page`` and ``Page.pager()``.


Notes
-------

Page numbers and item numbers start at 1. This concept has been used because users expect that the
first page has number 1 and the first item on a page also has number 1. So if you want to use the
page's items by their index number please note that you have to subtract 1.
"""

__author__ = "Christoph Haas"
__copyright__ = "Copyright 2007-2012 Christoph Haas"
__credits__ = ["Mike Orr"]
__license__ = "MIT"
__version__ = "0.4.0"
__maintainer__ = "Christoph Haas"
__email__ = "email@christoph-haas.de"
__status__ = "Beta"


import re
from string import Template


# Since the items on a page are mainly a list we subclass the "list" type
class Page(list):
    """A list/iterator representing the items on one page of a larger collection.

    An instance of the "Page" class is created from a _collection_ which is any
    list-like object that allows random access to its elements.

    The instance works as an iterator running from the first item to the last item on the given
    page. The Page.pager() method creates a link list allowing the user to go to other pages.

    A "Page" does not only carry the items on a certain page. It gives you additional information
    about the page in these "Page" object attributes:

    item_count
        Number of items in the collection

        **WARNING:** Unless you pass in an item_count, a count will be
        performed on the collection every time a Page instance is created.

    page
        Number of the current page

    items_per_page
        Maximal number of items displayed on a page

    first_page
        Number of the first page - usually 1 :)

    last_page
        Number of the last page

    previous_page
        Number of the previous page. If this is the first page it returns None.

    next_page
        Number of the next page. If this is the first page it returns None.

    page_count
        Number of pages

    items
        Sequence/iterator of items on the current page

    first_item
        Index of first item on the current page - starts with 1

    last_item
        Index of last item on the current page
    """
    def __init__(self, collection, page=1, items_per_page=20, item_count=None,
                 wrapper_class=None, url_maker=None, **kwargs):
        """Create a "Page" instance.

        Parameters:

        collection
            Sequence representing the collection of items to page through.

        page
            The requested page number - starts with 1. Default: 1.

        items_per_page
            The maximal number of items to be displayed per page.
            Default: 20.

        item_count (optional)
            The total number of items in the collection - if known.
            If this parameter is not given then the paginator will count
            the number of elements in the collection every time a "Page"
            is created. Giving this parameter will speed up things. In a busy
            real-life application you may want to cache the number of items.

        url_maker (optional)
            Callback to generate the URL of other pages, given its numbers.
            Must accept one int parameter and return a URI string.
        """
        if collection is not None:
            if wrapper_class is None:
                # Default case. The collection is already a list-type object.
                self.collection = collection
            else:
                # Special case. A custom wrapper class is used to access elements of the collection.
                self.collection = wrapper_class(collection)
        else:
            self.collection = []

        self.collection_type = type(collection)

        if url_maker is not None:
            self.url_maker = url_maker
        else:
            self.url_maker = self._default_url_maker

        # Assign kwargs to self
        self.kwargs = kwargs

        # The self.page is the number of the current page.
        # The first page has the number 1!
        try:
            self.page = int(page) # make it int() if we get it as a string
        except (ValueError, TypeError):
            self.page = 1

        self.items_per_page = items_per_page

        # Unless the user tells us how many items the collections has
        # we calculate that ourselves.
        if item_count is not None:
            self.item_count = item_count
        else:
            self.item_count = len(self.collection)

        # Compute the number of the first and last available page
        if self.item_count > 0:
            self.first_page = 1
            self.page_count = ((self.item_count - 1) // self.items_per_page) + 1
            self.last_page = self.first_page + self.page_count - 1

            # Make sure that the requested page number is the range of valid pages
            if self.page > self.last_page:
                self.page = self.last_page
            elif self.page < self.first_page:
                self.page = self.first_page

            # Note: the number of items on this page can be less than
            #       items_per_page if the last page is not full
            self.first_item = (self.page - 1) * items_per_page + 1
            self.last_item = min(self.first_item + items_per_page - 1, self.item_count)

            # We subclassed "list" so we need to call its init() method
            # and fill the new list with the items to be displayed on the page.
            # We use list() so that the items on the current page are retrieved
            # only once. In an SQL context that could otherwise lead to running the same
            # SQL query every time items would be accessed.
            try:
                first = self.first_item - 1
                last = self.last_item
                self.items = list(self.collection[first:last])
            except TypeError:
                raise TypeError("Your collection of type "+type(self.collection)+
                                " cannot be handled by paginate.")

            # Links to previous and next page
            if self.page > self.first_page:
                self.previous_page = self.page-1
            else:
                self.previous_page = None

            if self.page < self.last_page:
                self.next_page = self.page+1
            else:
                self.next_page = None

        # No items available
        else:
            self.first_page = None
            self.page_count = 0
            self.last_page = None
            self.first_item = None
            self.last_item = None
            self.previous_page = None
            self.next_page = None
            self.items = []

        # This is a subclass of the 'list' type. Initialise the list now.
        list.__init__(self, self.items)

    def __str__(self):
        return ("Page:\n"
            "Collection type:        {0.collection_type}\n"
            "Current page:           {0.page}\n"
            "First item:             {0.first_item}\n"
            "Last item:              {0.last_item}\n"
            "First page:             {0.first_page}\n"
            "Last page:              {0.last_page}\n"
            "Previous page:          {0.previous_page}\n"
            "Next page:              {0.next_page}\n"
            "Items per page:         {0.items_per_page}\n"
            "Total number of items:  {0.item_count}\n"
            "Number of pages:        {0.page_count}\n"
            ).format(self)

    def __repr__(self):
        return("<paginate.Page: Page {0}/{1}>".format(self.page, self.page_count))

    def pager(self, format='~2~', url=None, show_if_single_page=False, separator=' ',
        symbol_first='&lt;&lt;', symbol_last='&gt;&gt;', symbol_previous='&lt;', symbol_next='&gt;',
        symbol_dotdot='..', link_attr=dict(), curpage_attr=dict(), dotdot_attr=dict(),
        always_show_first=True, always_show_last=True):
        """
        Return string with links to other pages (e.g. '1 .. 5 6 7 [8] 9 10 11 .. 50').

        format:
            Format string that defines how the pager is rendered. The string
            can contain the following $-tokens that are substituted by the
            string.Template module:

            - $first_page: number of first reachable page
            - $last_page: number of last reachable page
            - $page: number of currently selected page
            - $page_count: number of reachable pages
            - $items_per_page: maximal number of items per page
            - $first_item: index of first item on the current page
            - $last_item: index of last item on the current page
            - $item_count: total number of items
            - $link_first: link to first page (unless this is first page)
            - $link_last: link to last page (unless this is last page)
            - $link_previous: link to previous page (unless this is first page)
            - $link_next: link to next page (unless this is last page)

            To render a range of pages the token '~3~' can be used. The
            number sets the radius of pages around the current page.
            Example for a range with radius 3:

            '1 .. 5 6 7 [8] 9 10 11 .. 50'

            Default: '~2~'

        url
            The URL that page links will point to. Make sure it contains the string
            $page which will be replaced by the actual page number.
            Must be given unless a url_maker is specified to __init__, in which
            case this parameter is ignored.

        symbol_first
            String to be displayed as the text for the $link_first link above.

            Default: '&lt;&lt;' (<<)

        symbol_last
            String to be displayed as the text for the $link_last link above.

            Default: '&gt;&gt;' (>>)

        symbol_previous
            String to be displayed as the text for the $link_previous link above.

            Default: '&lt;' (<)

        symbol_next
            String to be displayed as the text for the $link_next link above.

            Default: '&gt;' (>)

        symbol_dotdot
            String to be displayed as the text for ellipsis.

            Default: '..'

        separator:
            String that is used to separate page links/numbers in the above range of pages.

            Default: ' '

        show_if_single_page:
            if True the navigator will be shown even if there is only one page.

            Default: False

        link_attr (optional)
            A dictionary of attributes that get added to A-HREF links pointing to other pages. Can
            be used to define a CSS style or class to customize the look of links.

            Example: { 'style':'border: 1px solid green' }
            Example: { 'class':'pager_link' }

        curpage_attr (optional)
            A dictionary of attributes that get added to the current page number in the pager (which
            is obviously not a link). If this dictionary is not empty then the elements will be
            wrapped in a SPAN tag with the given attributes.

            Example: { 'style':'border: 3px solid blue' }
            Example: { 'class':'pager_curpage' }

        dotdot_attr (optional)
            A dictionary of attributes that get added to the '..' string in the pager (which is
            obviously not a link). If this dictionary is not empty then the elements will be wrapped
            in a SPAN tag with the given attributes.

            Example: { 'style':'color: #808080' }
            Example: { 'class':'pager_dotdot' }

        always_show_first (optional)
            Always show the first page number

        always_show_last (optional)
            Always show the last page number

        Additional keyword arguments are used as arguments in the links.
        """
        self.curpage_attr = curpage_attr
        self.separator = separator
        self.symbol_dotdot = symbol_dotdot
        self.link_attr = link_attr
        self.dotdot_attr = dotdot_attr
        self.url = url
        self.always_show_first = always_show_first
        self.always_show_last = always_show_last

        # Don't show navigator if there is no more than one page
        if self.page_count == 0 or (self.page_count == 1 and not show_if_single_page):
            return ''

        # Replace ~...~ in token format by range of pages
        result = re.sub(r'~(\d+)~', self._range, format)

        # Interpolate '$' variables
        result = Template(result).safe_substitute({
            'first_page': self.first_page,
            'last_page': self.last_page,
            'page': self.page,
            'page_count': self.page_count,
            'items_per_page': self.items_per_page,
            'first_item': self.first_item,
            'last_item': self.last_item,
            'item_count': self.item_count,
            'link_first': self.page>self.first_page and \
                    self._pagerlink(self.first_page, symbol_first) or '',
            'link_last': self.page<self.last_page and \
                    self._pagerlink(self.last_page, symbol_last) or '',
            'link_previous': self.previous_page and \
                    self._pagerlink(self.previous_page, symbol_previous) or '',
            'link_next': self.next_page and \
                    self._pagerlink(self.next_page, symbol_next) or ''
        })

        return result

    def _range(self, regexp_match):
        """
        Return range of linked pages (e.g. '1 2 [3] 4 5 6 7 8').

        Arguments:

        regexp_match
            A "re" (regular expressions) match object containing the
            radius of linked pages around the current page in
            regexp_match.group(1) as a string

        This function is supposed to be called as a callable in
        re.sub to replace occurences of ~\d+~ by a sequence of page links.
        """
        radius = int(regexp_match.group(1))

        # Compute the first and last page number within the radius
        # e.g. '1 .. 5 6 [7] 8 9 .. 12'
        # -> leftmost_page  = 5
        # -> rightmost_page = 9
        leftmost_page = max(self.first_page, (self.page-radius))
        rightmost_page = min(self.last_page, (self.page+radius))

        nav_items = []

        # Create a link to the first page (unless we are on the first page
        # or there would be no need to insert '..' spacers)
        if self.page != self.first_page and self.first_page < leftmost_page and self.always_show_first:
            nav_items.append( self._pagerlink(self.first_page, self.first_page) )

        # Insert dots if there are pages between the first page
        # and the currently displayed page range
        max_delta = 1 if self.always_show_first else 0
        if leftmost_page - self.first_page > max_delta:
            # Wrap in a SPAN tag if dotdot_attr is set
            text = self.symbol_dotdot
            if self.dotdot_attr:
                text = make_html_tag('span', **self.dotdot_attr) + text + '</span>'
            nav_items.append(text)

        for thispage in range(leftmost_page, rightmost_page+1):
            # Highlight the current page number and do not use a link
            if thispage == self.page:
                # Wrap in a SPAN tag if curpage_attr is set
                text = str(thispage)
                if self.curpage_attr:
                    text = make_html_tag('span', **self.curpage_attr) + text + '</span>'
                nav_items.append(text)
            # Otherwise create just a link to that page
            else:
                text = str(thispage)
                nav_items.append( self._pagerlink(thispage, text) )

        # Insert dots if there are pages between the displayed
        # page numbers and the end of the page range
        max_delta = 1 if self.always_show_last else 0
        if self.last_page - rightmost_page > max_delta:
            # Wrap in a SPAN tag if dotdot_attr is set
            text = self.symbol_dotdot
            if self.dotdot_attr:
                text = make_html_tag('span', **self.dotdot_attr) + text + '</span>'
            nav_items.append(text)

        # Create a link to the very last page (unless we are on the last
        # page or there would be no need to insert '..' spacers)
        if self.page != self.last_page and rightmost_page < self.last_page and self.always_show_last:
            nav_items.append( self._pagerlink(self.last_page, self.last_page) )

        return self.separator.join(nav_items)

    def _default_url_maker(self, page_number):
        if self.url is None:
            raise Exception(
                "You need to specify a 'url' parameter containing a '$page' placeholder.")

        if "$page" not in self.url:
            raise Exception("The 'url' parameter must contain a '$page' placeholder.")

        return self.url.replace('$page', str(page_number))

    def _pagerlink(self, page_number, text):
        """
        Create an A-HREF tag that points to another page.

        Parameters:

        page
            Number of the page that the link points to

        text
            Text to be printed in the A-HREF tag
        """
        target_url = self.url_maker(page_number)
        a_tag = make_html_tag('a', text=text, href=target_url, **self.link_attr)
        return a_tag


def make_html_tag(tag, text=None, **params):
    """Create an HTML tag string.

    tag
        The HTML tag to use (e.g. 'a', 'span' or 'div')

    text
        The text to enclose between opening and closing tag. If no text is specified then only
        the opening tag is returned.

    Example::
        make_html_tag('a', text="Hello", href="/another/page")
        -> <a href="/another/page">Hello</a>

    To use reserved Python keywords like "class" as a parameter prepend it with
    an underscore. Instead of "class='green'" use "_class='green'".

    Warning: Quotes and apostrophes are not escaped."""
    params_string = ''

    # Parameters are passed. Turn the dict into a string like "a=1 b=2 c=3" string.
    for key, value in params.items():
        # Strip off a leading underscore from the attribute's key to allow attributes like '_class'
        # to be used as a CSS class specification instead of the reserved Python keyword 'class'.
        key = key.lstrip('_')

        params_string += ' {0}="{1}"'.format(key, value)

    # Create the tag string
    tag_string = '<{0}{1}>'.format(tag, params_string)

    # Add text and closing tag if required.
    if text:
        tag_string += '{0}</{1}>'.format(text, tag)

    return tag_string
