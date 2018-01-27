"""Sample application demostrating SQL free functionality."""

# Websauna
import websauna.system


class RedisUser:
    pass


class RedisUserRegistry:
    pass


class Initializer(websauna.system.Initializer):
    """An initialization configuration used for starting myapp.

    Override parent class methods to customize application behavior.
    """

    def configure_templates(self):
        """Include our package templates folder in Jinja 2 configuration."""
        super(Initializer, self).configure_templates()

    def configure_views(self):
        """Configure views for your application.

        Let the config scanner to pick ``@simple_route`` definitions from scanned modules. Alternative you can call ``config.add_route()`` and ``config.add_view()`` here.
        """
        # We override this method, so that we route home to our home screen, not Websauna default one
        from . import views
        self.config.scan(views)

    def configure_models(self):
        """Register the models of this application."""
        from . import models
        self.config.scan(models)

    def configure_model_admins(self):
        """Register the models of this application."""

        # Call parent which registers user and group admins
        super(Initializer, self).configure_model_admins()

        # Scan our admins
        from . import admins
        self.config.scan(admins)

    def run(self):
        super(Initializer, self).run()
