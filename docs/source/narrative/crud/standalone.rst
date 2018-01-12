.. _crud-standalone:

===============
Standalone CRUD
===============

.. contents:: :local:

Introduction
============

This chapter describers how you can add a :ref:`CRUD` page set on your user facing website, outside the :ref:`admin` interface. In this example we create a simple CRUD to manage Ethereum smart contracts, based on a real world project. The contracts

* Can be viewed by anyone

* Can be added by signed in users

* Can be deleted by the owner (the user who added the contract)

* Contain some data which is retrofitted after the contract creation

The example code is guidelining and not a full, runnable, example.

.. image:: ../images/crud-listing.png
    :width: 640px

Sample model
------------

Below is the model code our CRUD allows to edit. In ``models.py``:

.. code-block:: python

    from decimal import Decimal

    import sqlalchemy as sa
    import sqlalchemy.orm as orm
    import sqlalchemy.dialects.postgresql as psql
    from sqlalchemy.orm import Session

    from websauna.system.model.columns import UTCDateTime
    from websauna.system.model.meta import Base
    from websauna.system.user.models import User
    from websauna.utils.time import now
    from websauna.wallet.models import Account, Asset, AssetNetwork


    class TokenContract(Base):
        """A standard Ethereum based token contract."""

        __tablename__ = "token_contract"

        id = sa.Column(psql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()"),)

        #: Legal name
        name = sa.Column(sa.String(256))

        #: When this was created
        created_at = sa.Column(UTCDateTime, default=now, nullable=False)

        #: When this data was updated last time
        updated_at = sa.Column(UTCDateTime, onupdate=now)

        #: Contract id as 256-bit int
        contract_address = sa.Column(sa.LargeBinary(length=20), unique=True)

        #: How many tokens this entity has total
        total_supply = sa.Column(sa.Integer, nullable=True)

        asset_id = sa.Column(sa.ForeignKey("asset.id"), nullable=True)
        asset = orm.relationship(Asset, backref=orm.backref("token_contract", uselist=False))

        owner_id = sa.Column(sa.ForeignKey("users.id"), nullable=True)
        owner = orm.relationship(User,
                            backref=orm.backref("token_contracts",
                                            lazy="dynamic",
                                            cascade="all, delete-orphan",
                                            single_parent=True,),
                            uselist=False)

Mapping CRUD to URL namespace
-----------------------------

In your :py:class:`websauna.system.Initializer` do:

.. code-block:: python

    def configure_views(self):
        """Configure views for your application."""

        # Add publicly facing contract CRUD interfaces under route name "contract".
        # This must come before scanning view or you'll get error at @view_config
        self.config.add_route('user-facing-contracts',
            '/contract/*traverse',
            factory="exampleapp.cruds.ContractCRUD.route_factory")

        from . import views
        self.config.scan(views)


Creating CRUD resources
-----------------------

In ``cruds.py`` we define resources, mappings, queries and permissions that will drive the views.

.. code-block:: python

    """Define CRUD traversable resources, model mapping and permissions. """

    from pyramid.decorator import reify
    from pyramid.security import Allow, Authenticated, Everyone, Deny

    import typing as t
    from sqlalchemy.orm import Query

    from websauna.system.core.root import Root
    from websauna.system.crud import Base64UUIDMapper
    from websauna.system.crud.sqlalchemy import CRUD
    from websauna.system.crud.sqlalchemy import Resource
    from websauna.system.http import Request

    from exampleapp.models import TokenContract
    from exampleapp.utils import bin_to_eth_address


    class ContractResource(Resource):
        """Map one TokenContract SQLAlchemy model instance to editable CRUD resource."""

        # __acl__ can be callable or property.
        # @reify caches the results after the first call
        @reify
        def __acl__(self) -> t.List[tuple]:
            # Give the user principal delete access as the owner
            # The returned list overrides __acl__ from the parent level
            # (ContractCRUD in our case)
            # See websauna.system.auth.principals for details
            contract = self.get_object()  # type: TokenContract
            if contract.owner:
                owner_principal = "user:{}".format(contract.owner.id)
                return [(Allow, owner_principal, "delete")]
            else:
                return []

        def get_title(self):
            token_contract = self.get_object()
            return "Smart contract {}".format(bin_to_eth_address(token_contract.contract_address))


    class ContractCRUD(CRUD):
        """A simple CRUD interface for adding new contracts to the system.

        """

        title = "Ethereum smart contracts"

        #: Pyramid access control list definitions
        __acl__ = [
            (Allow, Authenticated, "add"),  # Signed in users can add new contracts
            (Allow, Everyone, "view"),  # Anonymous user can list and view
            (Deny, Everyone, "edit"),  # Nobody can edit by default
            (Deny, Everyone, "delete"),  # Nobody can delete by default
        ]

        #: Which SQLAlchemy model we want CRUD for
        model = TokenContract

        #: Map URLs to SQLAlchemy using UUID attribute and base64
        mapper = Base64UUIDMapper(mapping_attribute="id")

        #: Tell what items we are storing inside this CRUD
        Resource = ContractResource

        def get_query(self) -> Query:
            """SQlAlchemy query to get all accessible items."""
            return self.request.dbsession.query(TokenContract)

        @staticmethod
        def route_factory(request: Request) -> Resource:
            """Route factory method for add_route.

            Put this CRUD in /contract under site root.
            """

            # Create instance of this CRUD
            crud = ContractCRUD(request)
            # This is the site traversing root object
            root = Root.root_factory(request)

            # Set up __parent__ and __name__ pointers required for traversal
            return Resource.make_lineage(root, crud, "contract")

Defining CRUD views
-------------------

We override the default SQLAlchemy views with custom fields.

.. code-block:: python

    import colander
    import deform
    from pyramid.httpexceptions import HTTPFound

    from websauna.system.crud import views as basecrudviews
    from websauna.system.crud import listing
    from websauna.system.crud.formgenerator import SQLAlchemyFormGenerator
    from websauna.system.http import Request
    from websauna.system.core.route import simple_route
    from websauna.system.core.viewconfig import view_overrides

    from exampleapp.cruds import ContractCRUD
    from exampleapp.models import TokenContract
    from exampleapp import task
    from exampleapp.schemas import validate_ethereum_address
    from exampleapp.utils import bin_to_eth_address, eth_address_to_bin


    @simple_route("/", route_name="home", renderer='exampleapp/home.html')
    def home(request: Request):
        """Render the contract listing at the site homepage."""

        # Redirect to the contract listing page
        return HTTPFound(request.route_url("user-facing-contracts", traverse="listing"))


    def get_human_readable_address(view, column, contract):
        """Get the Ethereum contract address in a human readable form."""
        return bin_to_eth_address(contract.contract_address)


    def get_human_readable_name(view, column, contract):
        """Get the name of asset the Ethereum contract is managing."""
        if not contract.asset:
            # We have not still fetched this information from Ethereum network
            return "---"
        return contract.asset.name


    def get_human_readable_symbol(view, column, contract):
        """Get the stock symbol of asset the Ethereum contract is managing."""
        if not contract.asset:
            # We have not still fetched this information from Ethereum network
            return "---"
        return contract.asset.symbol


    @view_overrides(context=ContractCRUD, route_name="user-facing-contracts")
    class ContractListing(basecrudviews.Listing):
        """List contracts in the database."""

        table = listing.Table(
            columns = [
                listing.Column("name", "Name", getter=get_human_readable_name),
                listing.Column("symbol", "Symbol", getter=get_human_readable_symbol),
                listing.Column("address", "Address", getter=get_human_readable_address),
                listing.ControlsColumn()
            ]
        )


    @view_overrides(context=ContractCRUD,
                    route_name="user-facing-contracts",
                    permission="add")
    class ContractAdd(basecrudviews.Add):
        """Add a new contract.

        Signed in users can add new contracts. Then they become owners of these contracts.
        """

        includes = [
            colander.SchemaNode(colander.String(),
                name='address',
                validator=validate_ethereum_address,
                description="Enter the address of an Ethereum standard token contract",
                widget=deform.widget.TextInputWidget(
                    template="textinput_placeholder",
                    placeholder="0x" + "0" * 40
                ),
            ),
        ]

        form_generator = SQLAlchemyFormGenerator(includes=includes)

        def initialize_object(self, form, appstruct: dict, contract: TokenContract):
            """Record values from the form on a freshly created object."""
            assert self.request.user
            address = appstruct["address"]
            address = eth_address_to_bin(address)
            contract.contract_address = address
            contract.owner = self.request.user

            # Trigger the delayed task to fill in asset information and such by
            # fetching it from Ethereum blockchain
            task.update_single_contract.apply_async(args=(self.request, bin_to_eth_address(address)))


    @view_overrides(context=ContractCRUD.Resource,
                    route_name="user-facing-contracts",
                    permission="view")
    class ContractShow(basecrudviews.Show):
        """Show a single contract.

        """

        includes = [
            "address",
            "updated_at",
            # Retrofit fields that the form generator could not automatically figure out
            colander.SchemaNode(colander.String(), name="symbol"),
            colander.SchemaNode(colander.String(), name="name"),
            colander.SchemaNode(colander.String(), name="total_supply", title="Tokens total"),
        ]

        form_generator = SQLAlchemyFormGenerator(includes=includes)

        def get_appstruct(self, form: deform.Form, form_context: TokenContract) -> dict:
            """Get the dictionary that populates the form."""
            fields = form.schema.dictify(form_context)
            contract = form_context
            if contract.asset:
                fields["symbol"] = contract.asset.symbol
                fields["name"] = contract.asset.name
                fields["total_supply"] = contract.total_supply
            else:
                fields["symbol"] = "(pending data from network)"
                fields["name"] = "(pending data from network)"
                fields["total_supply"] = "(pending data from network)"
            return fields

        def get_title(self):
            token_contract = self.get_object()
            return "Contract " + bin_to_eth_address(token_contract.contract_address)



    @view_overrides(context=ContractCRUD.Resource,
                    route_name="user-facing-contracts",
                    permission="delete")
    class ContractDelete(basecrudviews.Delete):
        """Confirmation screen to delete one contract.

        Shown only to the owner of the contract (the user who created the contract).
        See ContractResource for details.
        """

Validators
----------

We have also :term:`Colander` validator we place in ``schemas.py``:

.. code-block:: python

    import colander


    def validate_ethereum_address(node, value, **kwargs):
        """Make sure the user gives a valid ethereum hex address."""

        if not value.startswith("0x"):
            raise colander.Invalid(node, "Please enter a hex address starting using 0x")

        if not len(value) == 42:
            raise colander.Invalid(node, "Ethereum address must be 42 characters, including 0x prefix")
