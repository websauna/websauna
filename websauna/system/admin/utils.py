from websauna.system.admin import IAdmin


def get_admin(request) -> IAdmin:
    """Get hold of admin singleton."""
    admin_class = request.registry.queryUtility(IAdmin)
    return admin_class(request)


def get_admin_for_model(self, admin:IAdmin, model:object) -> Resource:



    for model_admin in self.model_admins.values():
        if model_admin.model == model:
            return model_admin

    raise KeyError("No admin defined for model: {}, got {} ".format(model, self.model_admins.values()))

