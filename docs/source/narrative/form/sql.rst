=======================
Forms based on SQL data
=======================

.. contents:: :local:

Introduction
============

The most common task of web forms is to input from and output data to a SQL database. Here are :term:`Deform` based recipes for common use cases.

Selection widget with SQL vocabulary
====================================

:py:class:`websauna.system.form.sqlalchemy.UUIDModelSel` provides a Colander schema type for matching (uuid, name) tuples to form elements and then back :term:`SQLAlchemy` objects. Furthermore a helper function :py:func:`websauna.system.form.sqlalchemy.convert_query_to_tuples` allows us to fill in a value vocabulary for select, radio or checkbox widget from a model query.

Assume ``models.py``:

.. code-block:: python

    class Customer(Organization):
        """A customer belonging to one user."""

        __tablename__ = "customer"

        id = Column(UUID(as_uuid=True),
                    primary_key=True,
                    server_default=sqlalchemy.text("uuid_generate_v4()"),)

        name = Column(String(256))
        phone_number = Column(String(256))
        business_id = Column(String(256))

        user_id = Column(ForeignKey("users.id"), nullable=False)
        user = relationship(User,
                            backref=backref("own_customers",
                                            lazy="dynamic",
                                            cascade="all, delete-orphan",
                                            single_parent=True,),
                            uselist=False)


And now we want to user to select from his or her customers on a Deform form:

.. code-block:: python

    import colander
    import deform
    from websauna.system.form.schema import CSRFSchema
    from websauna.system.form.sqlalchemy import UUIDModelSet, convert_query_to_tuples
    from websauna.system.core.route import simple_route

    from .models import Customer


    def customers_by_user_widget(node: colander.SchemaNode, kw: dict):
        """Populate selection widget vocabulary with user's customers.

        :param node: The currrent :py:class:`colandar.SchemaNode` for which we are evaluation this.

        :param kw: ``schema.bind()`` arguments passed around.
        """
        request = kw["request"]
        user = request.user
        dbsession = request.dbsession
        query = dbsession.query(Customer).filter(Customer.user == user)
        vocab = convert_query_to_tuples(query, first_column="id", second_column="name")
        return deform.widget.SelectWidget(values=vocab)



    class ChooseCustomer(CSRFSchema):
        """A form with a widget to choose one of existing customers of a user."""

        customer =  colander.SchemaNode(

                # Convert selection widget UUIDs back to Customer objects
                UUIDModelSet(model=Customer, match_column="id"),

                title="Choose your customers",

                # A SelectWidget with values lazily populated
                widget=customers_by_user_widget)


    @simple_route("/choose-customer",
        route_name="choose_customer",
        renderer='nordledger/choose_customer.html')
    def choose_customer(request: Request):
        """Render an invoice creation form."""

        schema = ChooseCustomer()
        schema = schema.bind(request=request)
        form = deform.Form(schema, buttons=("submit",))
        rendered_form = form.render()

        return locals()
