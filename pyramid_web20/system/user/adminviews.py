from pyramid.view import view_config

from .admin import UserAdmin


@view_config(context=UserAdmin, name="", renderer="string", permission='view', route_name="admin")
def user_listing(context, request):
    return {"x": "y"}

