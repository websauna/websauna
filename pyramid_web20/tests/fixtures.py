import pytest

from fixture.loadable import EnvLoadableFixture
from fixture.style import NamedDataStyle

import transaction

from pyramid import testing

from .. import models


class LoadOnlyFixture(EnvLoadableFixture):
    def __init__(self, session=None, **kw):
        EnvLoadableFixture.__init__(self, **kw)
        self.session = session

    def commit(self):
        pass

    def rollback(self):
        pass

    class Medium(EnvLoadableFixture.Medium):
        def visit_loader(self, loader):
            self.session = loader.session

        def save(self, row, column_vals):
            obj = self.medium()
            for c, val in column_vals:
                setattr(obj, c, val)
            self.session.add(obj)
            return obj

        def clear(self, obj):
            pass


dbfixture = LoadOnlyFixture(
    env = models,
    style = NamedDataStyle(),
    session = models.DBSession
)