from pyramid.view import view_config

from .admin import UserAdmin
from pyramid_layout.panel import panel_config

from pyramid_web20 import DBSession


@panel_config(name='admin_panel', context=UserAdmin, renderer='admin/user_panel.html')
def default_model_admin_panel(context, request):
    model_admin = context
    admin = model_admin.__parent__
    model = model_admin.get_model()

    title = model_admin.title
    count = DBSession.query(model).count()
    latest_user = DBSession.query(model).order_by(model.activated_at.desc()).first()
    latest_user_url = request.resource_url(admin.get_admin_resource(latest_user))

    return locals()
