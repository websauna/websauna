import sys
from setuptools import setup, find_packages
from codecs import open
from os import path

assert sys.version_info >= (3,4), "Websauna needs Python 3.4 or newer, you have {}".format(sys.version_info)

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='websauna',
    namespace_packages=["websauna"],

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.0',

    description=long_description.split()[0],
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/websauna/websauna',

    # Author details
    author='Mikko Ohtamaa',
    author_email='mikko@opensourcehacker.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='sqlalchemy postgresql pyramid pytest',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['docs']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[

        # Pyramid dependencies
        'pyramid>=1.6',
        'waitress',
        'websauna.viewconfig',
        'pyramid_redis_sessions',
        'pyramid-layout',
        "deform>=2.0a2",
        'pyramid_deform',
        "pyramid_debugtoolbar",
        "pyramid_jinja2",
        "ipython[notebook]<4",
        "pyramid_ipython",
        "scandir",  # os.scandir backport for py3.4

        # Time handling
        "arrow",
        "pytz",

        # SQLAlchemy and database support
        "psycopg2",
        "sqlalchemy",
        "alembic",
        "colanderalchemy",
        "pyramid_tm",
        "jsonpointer",
        "pgcli",

        # User management
        "horus",
        "authomatic",

        # Email
        'pyramid-mailer',
        'premailer',

        # Tasks
        'pyramid_celery',

        # Python 3.4 typing
        "backports.typing",

        # Needed by python_notebook etc. who call pyramid.paster module
        "pyramid_notebook>=0.1.6",
        "PasteDeploy",

        # Console logging
        "rainbow_logging_handler"
    ],

    # List additional groups of  dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['check-manifest', 'Sphinx', 'sphinx-autoapi', 'setuptools_git', 'zest.releaser', 'sphinx-autodoc-typehints', 'pyramid_autodoc', "sphinx_rtd_theme", "sphinxcontrib-zopeext"],
        'test': ['pytest>=2.8', 'coverage', 'webtest', 'pytest-splinter', 'pytest-timeout', 'pytest-cov', "codecov", "flaky"],
    },

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'ws-sync-db=websauna.system.devop.scripts.syncdb:main',
            'ws-db-shell=websauna.system.devop.scripts.dbshell:main',
            'ws-shell=websauna.system.devop.scripts.shell:main',
            'ws-tweens=websauna.system.devop.scripts.tweens:main',
            'ws-alembic=websauna.system.devop.scripts.alembic:main',
            'ws-dump-db=websauna.system.devop.scripts.dumpdb:main',
            'ws-create-user=websauna.system.devop.scripts.createuser:main',
            'ws-celery=websauna.system.devop.scripts.celery:main',
            'ws-pserve=websauna.system.devop.scripts.pserve:main',
            'ws-create-table=websauna.system.devop.scripts.createtable:main',
            'ws-sanity-check=websauna.system.devop.scripts.sanitycheck:main',
            'ws-collect-static=websauna.system.devop.scripts.collectstatic:main',
        ],

        'paste.app_factory': [
            'main=websauna.system:main',

            # Scheduler auomated test suite entry point
            'scheduler_test=websauna.tests.test_scheduler:main',
            'tutorial_test=websauna.tests.tutorial:main',
        ],

        'pyramid.scaffold': [
            "websauna_app=websauna.scaffolds:App",
            "websauna_addon=websauna.scaffolds:Addon",
        ]
    },
)
