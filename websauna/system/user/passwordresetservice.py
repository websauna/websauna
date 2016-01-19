
class DefaultPasswordResetService:

    def create_forgot_password_email(self, request, email) -> Response:
        """Create a new email activation token for a user and produce the following screen."""

        dbsession = request.dbsession
        user_service = get_user_service(request.registry)
        user = self.get_by_email(request, email)

        Activation = get_activation_model(request.registry)
        activation = Activation()
        dbsession.add(activation)
        dbsession.flush()
        user.activation = activation

        assert user.activation.code, "Could not generate the password reset code"
        link = request.route_url('reset_password', code=user.activation.code)

        context = dict(link=link, user=user)
        send_templated_mail(request, [user.email], "login/email/forgot_password", context=context)

        messages.add(request, msg="Please check your email to continue password reset.", kind='success', msg_id="msg-check-email")
        return HTTPFound(location=self.reset_password_redirect_view)
