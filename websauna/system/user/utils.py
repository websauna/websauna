from websauna.system.user.interfaces import IGroupClass, IUserClass


def get_user_class(registry):
    user_class = registry.queryUtility(IUserClass)
    return user_class


def get_group_class(registry):
    group_class = registry.queryUtility(IGroupClass)
    return group_class

