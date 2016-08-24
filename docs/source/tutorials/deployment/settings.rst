========
Settings
========

Introduction
============

Playbook comes with plethora of knobs to turn and tune.

Variable catalog
================

See `default.yml <https://github.com/websauna/websauna.ansible/blob/master/default.yml>`_.

Variable ordering
=================

`To understand how settings are applied it is important to know in which order Ansible evaluates different variables and configuration files <http://docs.ansible.com/ansible/playbooks_variables.html#variable-precedence-where-should-i-put-a-variable>`_.

Generally the order is this

* In ``vars`` section of your ``playbook.yml`` you put the basic settings which cannot be deduced from the context (``git_repository``)

* Then we include ``secrets.yml`` vault with all passwords and API tokens

* Then we apply ``defaults.yml`` which generates a lot of variables based on ``vars`` input which you usually don't want to tune (database name, username, log file locations, etc.)

* If you are unhappy with ``defaults.yml`` results, you can create and include yet another file ``local-config.yml`` which overrides these

* Now you can still apply host and group specific variables as per Ansible manual
