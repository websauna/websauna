"""Generate Ansible playbook variable reference.

* Variables are defined in .yml files which are included in playbook

* The variable is described in the precedenting comment

* The first variable in a playbook must be ``config_description`` which gives the description of the playbook

* Section headers using the format below are stripped out::

    # ----------------------------------------------------
    # Log watch
    # ----------------------------------------------------

* We have separate variable files for required, optional an default variables

"""
# Standard Library
import os
import sys
from collections import OrderedDict

# Pyramid
import jinja2

import ruamel.yaml
from ruamel.yaml.comments import CommentedSeq
from ruamel.yaml.tokens import CommentToken


TEMPLATE = """
==================
Playbook variables
==================

.. _playbook-vars:

This is a reference of available Ansible Playbook variables for ``websauna.ansible`` playbook. See :ref:`deployment documentation <deployment>` for more information.

.. raw:: html

    <!-- Make TOC more readable -->
    <style>

        #contents ul > li {
            font-weight: bold;
            margin-top: 20px;
        }

        #contents ul > li > ul {
            font-weight: normal;
            margin-top: 0;

            display: flex;
            flex-wrap: wrap;
            /* TODO: Width here does not seem to take effect, forcing it below */
            flex: 1 0 200px;
            font-size: 90%;
        }

        #contents ul > li > ul > li {

            font-weight: normal;
            margin-top: 0;


            list-style: none;
            margin-left: 0;
            margin-right: 20px;
            box-sizing: border-box;
            width: 250px;
        }

    </style>


.. contents:: :local:

{% for title, module in modules.items() %}

{# Heading of a section #}
{{ title }}
{{ "=" * title|length }}

{{ module.description }}

{# All variables in a section #}
{% for name, content in module.vars.items() %}

.. _playbook-{{ name }}:

{{ name }}
{{ "-" * name|length }}

{{ content.comment }}

{% if content.value %}
*Default value*::

{{ content.value|outindent }}

{% else %}
*Default value not set.*
{% endif %}

{% endfor %}
{% endfor %}
"""


@jinja2.contextfilter
def outindent(jinja_ctx, context: str, **kw):
    """Jinja filter to add 4 spaces to the beginning of each line."""

    # YAML parsers exposes lists as is
    if isinstance(context, CommentedSeq):
        result = ""
        for item in context:
            result += " - " + str(item) + "\n"
        context = result

    if type(context) != str:
        context = str(context)

    lines = context.split("\n")
    new_lines = ["    " + line for line in lines]
    return "\n".join(new_lines)


env = jinja2.Environment()
env.filters["outindent"] = outindent

template = env.from_string(TEMPLATE)


def strip_indent(doc):
    lines = doc.split("\n")

    def strip_prefix(line):
        if line.startswith("    "):
            return line[4:]
        return line

    return "\n".join([strip_prefix(l) for l in lines])


def flatten_comment(seq):
    """Flatten a sequence of comment tokens to a human-readable string."""

    # "[CommentToken(value='# Extra settings placed in ``[app:main]`` section in generated production.ini.\\n'), CommentToken(value='# Example:\\n'), CommentToken(value='#\\n'), CommentToken(value='# extra_ini_settings: |\\n'), CommentToken(value='#     mail.host = mymailserver.internal\\n'), CommentToken(value='#     websauna.superusers =\\n'), CommentToken(value='#         mikko@example.com\\n'), CommentToken(value='#\\n')]

    if not seq:
        return ""

    result = []
    for item in seq:
        if not item:
            continue
        if isinstance(item, CommentToken):

            # Mangle away # comment start from the line
            s = item.value
            s = s.strip(" ")
            s = s.lstrip("#")
            s = s.rstrip("\n")

            if s.startswith(" "):
                s = s[1:]

            result.append(s)

    if result:
        raw_comment = "\n".join(result)
    else:
        return ""

    section_header = raw_comment.rfind("---")
    if section_header >= 0:
        raw_comment = raw_comment[section_header + 3:]

    return raw_comment


def find_yaml_commented_vars(playbook_file: str):
    """Extract variables and their descriptions from a Playbook file.

    :param playbook_file:
    :return: tuple (playbook config_description, variables as name: {comment, value}
    """
    playbook_file = os.path.abspath(playbook_file)
    vars = OrderedDict()
    with open(playbook_file, "rt") as inp:
        data = ruamel.yaml.load(inp, ruamel.yaml.RoundTripLoader)
        for key, value in data.items():

            comment_data = data.ca._items.get(key)

            if comment_data:
                # [None, seq of comment tokens]
                comment = flatten_comment(comment_data[1])
            else:
                comment = ""

            if not comment:
                if key != "config_description":
                    print("No description provided for a variable {} in {}".format(key, playbook_file), file=sys.stderr)
                    comment = "No description provided at the moment."

            vars[key] = {"comment": comment, "value": value}

    if 'config_description' not in vars:
        print("Playbook doesn't provide config_description ", playbook_file, file=sys.stderr)

    config_description = vars.pop("config_description", None)
    if config_description:
        description = config_description["value"]
    else:
        description = "No description"

    vars = OrderedDict(sorted(vars.items(), key=lambda x: x[0]))

    return {"description": description, "vars": vars}


# Assume we have checked out websauna.ansible to the same folder as websauna
modules = OrderedDict()
modules["Required"] = find_yaml_commented_vars("../../websauna.ansible/required.yml")
modules["Optional"] = find_yaml_commented_vars("../../websauna.ansible/optional.yml")
modules["Default"] = find_yaml_commented_vars("../../websauna.ansible/default.yml")


print(template.render(dict(modules=modules)))
