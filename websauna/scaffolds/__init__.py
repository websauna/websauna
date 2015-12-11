"""Scaffold template definitions."""
from pyramid.scaffolds import PyramidTemplate


class App(PyramidTemplate):
    _template_dir = 'app'
    summary = 'Websauna app'


class Addon(PyramidTemplate):
    _template_dir = 'addon'
    summary = 'Websauna addon'