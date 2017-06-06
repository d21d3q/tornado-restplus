# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class Namespace(object):
    '''
    Group resources together.

    Namespace allows for gourping several endpoints.

    :param str name: The namespace name
    :param str description: An optionale short description
    :param str path: An optional prefix path. If not provided, prefix is ``/+name``
    :param list decorators: A list of decorators to apply to each resources
    :param bool validate: Whether or not to perform validation on this namespace
    :param Api api: an optional API to attache to the namespace
    '''
    def __init__(self, name, description=None, path=None, decorators=None,
                 validate=None, **kwargs):
        self.name = name
        self.description = description
        self._path = path

        self._schema = None
        self._validate = validate
        self.models = {}
        # self.urls = {}
        # self.decorators = decorators if decorators else []
        self.resources = []
        self.error_handlers = {}
        self.default_error_handler = None
        self.apis = []
        if 'api' in kwargs:
            self.apis.append(kwargs['api'])

    @property
    def path(self):
        return (self._path or ('/' + self.name)).rstrip('/')

    def add_resource(self, resource, *urls, **kwargs):
        '''
        Register a Resource for a given API Namespace

        :param Resource resource: the resource ro register
        :param str urls: one or more url routes to match for the resource,
                         standard flask routing rules apply.
                         Any url variables will be passed to the resource method as args.
        :param str endpoint: endpoint name (defaults to :meth:`Resource.__name__.lower`
            Can be used to reference this route in :class:`fields.Url` fields
        :param list|tuple resource_class_args: args to be forwarded to the constructor of the resource.
        :param dict resource_class_kwargs: kwargs to be forwarded to the constructor of the resource.

        Additional keyword arguments not specified above will be passed as-is
        to :meth:`flask.Flask.add_url_rule`.

        Examples::

            namespace.add_resource(HelloWorld, '/', '/hello')
            namespace.add_resource(Foo, '/foo', endpoint="foo")
            namespace.add_resource(FooSpecial, '/special/foo', endpoint="foo")
        '''
        self.resources.append((resource, urls, kwargs))
        for api in self.apis:
            ns_urls = api.ns_urls(self, urls)
            api.register_resource(self, resource, *ns_urls, **kwargs)

    def route(self, *urls, **kwargs):
        '''
        A decorator to route resources.
        '''
        def wrapper(cls):
            # doc = kwargs.pop('doc', None)
            # if doc is not None:
            #     self._handle_api_doc(cls, doc)
            self.add_resource(cls, *urls, **kwargs)
            return cls
        return wrapper
