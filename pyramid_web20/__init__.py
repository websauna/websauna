from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from . import models
from . import views


def configure_horus(config):
    # Tell horus which SQLAlchemy scoped session to use:
    from hem.interfaces import IDBSession
    registry = config.registry
    registry.registerUtility(models.DBSession, IDBSession)

    config.include('horus')
    config.scan_horus(models)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    models.DBSession.configure(bind=engine)
    models.Base.metadata.bind = engine
    config = Configurator(settings=settings)

    # Jinja 2 templates as .html files
    config.include('pyramid_jinja2')
    config.add_jinja2_renderer('.html')
    config.add_jinja2_search_path('pyramid_web20:templates', name='.html')

    config.add_static_view('static', 'static', cache_max_age=3600)

    configure_horus(config)

    config.add_route('home', '/')
    config.scan()
    config.scan(views)

    return config.make_wsgi_app()
